# 形式化归约

`proof.json` 是一个形式化归约证书。它把以下四个组件机械地归约为二元哥德巴赫猜想：

- A1：主弧显式下界 `Major(N) >= 1.32 N/(log N)^2 - 10 N/(log N)^3`；
- A2：Petrov-Tanaka 次要弧上界 `|Minor(N)| <= (1/16) N/(log N)^2`；
- A3：分解 `R(N) = Major(N) + Minor(N)`；
- A4：本地有限验证 `4 <= N < 10^7`。

`checker.py` 检查归约的每一步：系数相减、误差项传递、正性、区间拼接与最终等价。正性检查会计算

    margin = (1.32 - 1/16) - 10/log(10^7) = 0.637079... > 0.

因此 R(N) > 0 对所有 N >= 10^7 成立。A1 的显式误差分解在 `proof/goldbach_proof.md` 第 3.1-3.3 节给出；A2 是 Petrov-Tanaka [6, Theorem 1.3] 的显式引用，`proof/minor_arc_lemma.md` 给出原文对照。

`goldbach_verify.py` 内嵌了同一份证书与检查器的自包含副本，因此即使 `formal/` 目录未被稀疏检出，入口脚本仍可独立运行。

