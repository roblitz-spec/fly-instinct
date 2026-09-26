"""
fly_instinct.py — “本能引擎” (Instinct Engine)
================================================

一个可复用、非学习的“本能”信号源。

核心思想（储备池计算 / Reservoir Computing）：
  用一个【权重冻结、不学习】的递归网络，把输入刺激打散成
  高维、非平凡、结构化的“本能反应”。它既不是白噪声（死的），
  也不是脚本规则（可预测），而是“像活物一样对刺激有反应”。

真实完整版会加载 MaleCNS 连接组（~16.67 万神经元）的某个采样子图
作为冻结网络；本 PoC 用一个【结构匹配的冻结递归网络】扮演这个角色，
接口与行为完全一致，后续可直接替换为真实连接组子图。

用法：
    from fly_instinct import FlyInstinct
    fly = FlyInstinct(n_neurons=150, seed=7)
    reaction, spikes = fly.react(stimulus)      # stimulus: 1D/2D 数组

设计原则：
  - 权重在 __init__ 时生成后【永久冻结】，react() 不做任何学习。
  - 给定 seed + 刺激，输出是【确定性的】（除非显式注入噪声）。
  - 噪声是可选的：真实动物的本能也带一点热噪声，可加可不加。
"""

from __future__ import annotations
import numpy as np


class FlyInstinct:
    """冻结递归网络 + LIF 动力学 组成的“本能”信号源。"""

    def __init__(self, n_neurons: int = 150, n_input: int = 1,
                 n_output: int = 1, seed: int = 0,
                 tau: float = 20.0, dt: float = 1.0,
                 v_th: float = 1.0, v_reset: float = 0.0,
                 gain: float = 6.0, spectral_radius: float = 0.95):
        self.n = n_neurons
        self.n_in = n_input
        self.n_out = n_output
        self.tau = tau
        self.dt = dt
        self.v_th = v_th
        self.v_reset = v_reset
        self.gain = gain

        rng = np.random.default_rng(seed)

        # 递归权重：冻结的“本能回路”。缩放到临界点附近以保留丰富动力学。
        W = rng.normal(0.0, 1.0, size=(n_neurons, n_neurons))
        W *= spectral_radius / np.linalg.norm(W, ord=2)

        # 输入权重：刺激 -> 网络。
        Win = rng.normal(0.0, 1.0, size=(n_neurons, n_input)) * (1.0 / np.sqrt(n_input + 1.0))

        # 读出权重：网络活动 -> 单一“反应”标量（冻结，不训练）。
        Wout = rng.normal(0.0, 1.0, size=(n_output, n_neurons)) / np.sqrt(n_neurons)

        # —— 冻结：之后不再改变 ——
        self.W = W
        self.Win = Win
        self.Wout = Wout
        self._rng = np.random.default_rng(seed + 1)

        self._v = np.zeros(n_neurons)
        self._sp_prev = np.zeros(n_neurons)
        self._reset_internal()

    def _reset_internal(self):
        self._v = np.zeros(self.n)
        self._sp_prev = np.zeros(self.n)

    def reset(self):
        """清空网络内部状态（保留冻结权重）。"""
        self._reset_internal()

    def step(self, stimulus: np.ndarray, noise: float = 0.0) -> np.ndarray:
        """推进一个时间步，返回该步的“反应”标量数组（长度 n_out）。"""
        stim = np.asarray(stimulus, dtype=float).ravel()
        I = self.W @ self._sp_prev + self.Win @ stim
        if noise and noise > 0.0:
            I = I + self._rng.normal(0.0, noise, size=self.n)
        self._v = self._v + (self.dt / self.tau) * (0.0 - self._v) + self.dt * (I * self.gain)
        sp = (self._v >= self.v_th).astype(float)
        self._v = np.where(sp == 1.0, self.v_reset, self._v)
        self._sp_prev = sp
        return (self.Wout @ sp.T).ravel()

    def react(self, stimulus: np.ndarray, noise: float = 0.0,
              smooth: int = 1, track_spikes: bool | None = None):
        """
        对一段刺激序列做"本能反应"。

        参数
        ----
        stimulus : 1D 或 2D 数组，形状 (T,) 或 (T, n_input)
        noise    : 注入的网络内噪声幅度（0=确定性）
        smooth   : 输出滑动平均窗宽（1=不平滑）
        track_spikes : 是否记录每个神经元的发放矩阵 (n,T)。
                   None=自动（n*T < 1 亿时记录，否则跳过以节省内存）。

        返回
        ----
        reaction : (T,) 反应强度序列（静息基线对齐 0、峰值对齐 1；
                   若网络被抑制到低于静息水平会出现小幅负值）
        spikes   : (n, T) 每个神经元的发放（0/1），供可视化；
                   大网络（track_spikes=False）时返回 None
        """
        stimulus = np.asarray(stimulus, dtype=float)
        if stimulus.ndim == 1:
            stimulus = stimulus[:, None]
        T = stimulus.shape[0]
        self.reset()

        # 自动判断：n*T 超过 1 亿元素（~800MB float64）就不记录尖峰矩阵
        if track_spikes is None:
            track_spikes = (self.n * T) < 100_000_000

        # 先测静息读出（零输入，待动力学稳定后取均值），作为反应基线
        for _ in range(max(10, int(self.tau))):
            self.step(np.zeros(self.n_in), noise=0.0)
        resting = float((self.Wout @ self._sp_prev).ravel()[0])

        reaction = np.zeros(T)
        spikes = np.zeros((self.n, T)) if track_spikes else None
        for t in range(T):
            reaction[t] = self.step(stimulus[t], noise=noise)[0] - resting
            if track_spikes:
                spikes[:, t] = self._sp_prev

        if smooth > 1:
            k = min(smooth, T)
            kernel = np.ones(k) / k
            reaction = np.convolve(reaction, kernel, mode="same")

        # 归一化：静息基线对齐 0，峰值对齐 1（便于跨项目复用）
        peak = reaction.max()
        if peak > 0:
            reaction = reaction / peak
        return reaction, spikes

    @classmethod
    def from_malecns(cls, edges_path, ann_path=None, nt_path=None,
                     seed=0, in_neurons=800, tau=20.0, dt=1.0,
                     v_th=1.0, v_reset=0.0, gain=1.0, spectral_radius=0.9):
        """
        用【真实 MaleCNS 稀疏连接组】作为冻结递归核心构造本能引擎。

        - 递归权重 W：真实连接组（按递质赋兴奋/抑制符号，谱半径归一到临界点），永久冻结。
        - 输入接口 Win：刺激 -> 顶层 out-degree 神经元的固定兴奋投影（冻结、非学习）。
        - 读出接口 Wout：全部神经元 -> 单一反应标量的固定随机投影（冻结、非学习）。
          （该子集未标注明确的感受/运动神经元，用冻结投影是诚实且非学习的做法。）

        与替身版接口完全一致：fly.react(stimulus) -> (reaction, spikes)
        """
        from .loader import load_malecns

        d = load_malecns(edges_path, ann_path, nt_path,
                         spectral_radius=spectral_radius)
        return cls.from_loaded(d, seed=seed, in_neurons=in_neurons,
                               tau=tau, dt=dt, v_th=v_th, v_reset=v_reset,
                               gain=gain, spectral_radius=spectral_radius)

    @classmethod
    def from_loaded(cls, d: dict, seed=0, in_neurons=800, tau=20.0, dt=1.0,
                    v_th=1.0, v_reset=0.0, gain=1.0, spectral_radius=0.9):
        """
        由 loader 产出的 dict（含 W/n/n_edges/inhibit_frac/sr_raw）组装引擎。
        与 from_malecns 共享同一套接口与动力学；CSV 子集版与完整 feather 版
        都走这里，区别只在 dict 来自 load_malecns 还是 load_full_feather。
        """
        from scipy import sparse

        W = d["W"]
        n = d["n"]

        obj = cls.__new__(cls)
        obj.n = n
        obj.n_in = 1
        obj.n_out = 1
        obj.tau = tau
        obj.dt = dt
        obj.v_th = v_th
        obj.v_reset = v_reset
        obj.gain = gain
        obj.W = W  # 冻结：真实连接组

        rng = np.random.default_rng(seed)

        # 输入接口：刺激投到顶层 out-degree 神经元（兴奋驱动）
        # 直接用 CSR 的 indices（列下标）算 out-degree，避免 W.tocoo() 的整份拷贝
        outdeg = np.bincount(W.indices, minlength=n)
        order = np.lexsort((np.arange(n), -outdeg))  # out-degree 降序，同度按 idx 升序
        top = order[:min(in_neurons, n)]
        in_w = rng.uniform(0.6, 1.2, size=top.size)
        Win = sparse.csr_matrix((in_w, (top, np.zeros(top.size, dtype=int))),
                                shape=(n, 1))

        # 读出接口：固定随机投影 -> 单一反应
        Wout = sparse.csr_matrix(rng.normal(0.0, 1.0, (1, n)) / np.sqrt(n))

        obj.Win = Win
        obj.Wout = Wout
        obj._rng = np.random.default_rng(seed + 1)
        obj._v = np.zeros(n)
        obj._sp_prev = np.zeros(n)

        obj.is_real = True
        obj.meta = {
            "n_nodes": n,
            "n_edges": d["n_edges"],
            "inhibit_frac": d["inhibit_frac"],
            "sr_raw": d["sr_raw"],
            "sr_target": spectral_radius,
            "in_neurons": int(top.size),
        }
        return obj
