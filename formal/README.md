# 形式化归约

`proof.json` 是一个形式化归约证书。`goldbach_verify.py` 内嵌了同一份证书与检查器的自包含副本，因此即使 `formal/` 目录未被稀疏检出，入口脚本仍可独立运行。`proof.json` 与 `checker.py` 是供人工阅读的可读副本。它把以下四个组件机械地归约为二元哥德巴赫猜想：

- A1：主弧下界；
- A2：次要弧上界；
- A3：R(N) 的分解；
- A4：有限验证。

`checker.py` 检查归约的每一步：系数相减、正性、区间拼接与最终等价。A1 与 A2 的解析证明分别在 `proof/goldbach_proof.md` 的定理 3.1 与 `proof/minor_arc_lemma.md` 的定理 6.1 中给出。

这种拆分是刻意的：解析估计与纯逻辑归约分开，便于独立复核。若 A1、A2、A4 都成立，则 checker 验证的归约保证最终结论成立。

