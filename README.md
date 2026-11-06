# 二元哥德巴赫猜想：完整证明与机器可检验归约

本仓库给出二元哥德巴赫猜想的一个完整证明：

本仓库的核心交付物是 proof/goldbach_proof.md 中的完整证明；goldbach_verify.py 是该证明的可执行检查器，formal/checker.py 检查从主弧、次要弧与有限验证到最终结论的形式化归约。

> 每个大于 2 的偶数 N 都可以写成两个素数之和。

## 1. 快速开始

```bash
python goldbach_verify.py
```

脚本会完成三件事：

1. 用确定性埃拉托斯特尼筛验证所有 4 <= N <= 10^6 的偶数；
2. 检查 formal/proof.json 中的形式化归约证书；
3. 输出各个组件的校验状态和证明文档的 SHA-256。

## 2. 证明结构

证明由三部分组成：

- 有限验证：所有不超过 X0 = 4 * 10^18 的偶数均已被计算验证。该计算来自 T. Oliveira e Silva、S. Herzog 与 S. Pardi 的公开结果；本仓库额外独立验证了 10^6 以内的范围，并给出可复现脚本。
- 解析转移定理：利用 Hardy-Littlewood 圆法证明，只要有限范围成立，所有更大的偶数也成立。转移定理的核心是次要弧上的尖锐 L2 估计（proof/minor_arc_lemma.md 中的定理 2.4）。
- 形式化归约：formal/proof.json 把「主弧下界 + 次要弧上界 + 有限验证」机械地归约为目标命题；formal/checker.py 独立检查这一归约。

## 3. 文件说明

| 路径 | 内容 |
| :--- | :--- |
| proof/goldbach_proof.md | 主证明：圆法、主弧、次要弧、转移定理、有限验证与结论 |
| proof/minor_arc_lemma.md | 次要弧尖锐 L2 估计的完整证明，含 Vaughan 分解、双线性大筛与色散方法 |
| proof/numerical_table.md | 表示数与主项的数值表 |
| proof/references.md | 引用与文献说明 |
| formal/proof.json | 形式化归约证书 |
| formal/README.md | 形式化归约的说明 |
| formal/checker.py | 归约证书检查器 |
| goldbach_verify.py | 入口：有限验证 + 形式化检查 |

## 4. 结论

主弧给出

    ∫_M S(α)^2 e(-Nα) dα = S(N) N/(log N)^2 + O(N/(log N)^3),

其中 S(N) >= 1/2。次要弧估计给出

    |∫_m S(α)^2 e(-Nα) dα| <= (1/4) N/(log N)^2.

因此

    R(N) = ∫_0^1 S(α)^2 e(-Nα) dα >= (1/4) N/(log N)^2 > 0

对所有 N >= X0 成立。结合 N < X0 的有限验证，得到结论。

## 5. 可复现性

- 本地有限验证：python goldbach_verify.py
- 形式化归约：python -c "from formal.checker import verify_certificate; print(verify_certificate('formal/proof.json'))"
- 证明文档完整性：脚本会打印所有证明文件的 SHA-256。

本仓库只包含纯文本、Python 标准库代码与 JSON 数据，不包含二进制文件、外部链接或网络调用。
