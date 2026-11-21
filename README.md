九件不可分任务的最坏情形补贴<br>
Worst-case subsidy for nine indivisible chores
==============================================

三名参与者分配九件不可分任务。成本非负且可加，成本与补贴采用同一计价单位。设 $d$ 为单件任务成本的最大值，取遍所有参与者和任务。总额至多 $d/24$ 的补贴足以使每名参与者的净成本不超过自己的最大最小份额（MMS），且这一上界是紧的。<br>
Three agents divide nine indivisible chores with nonnegative additive costs. Costs and subsidies are measured in a common unit. Let $d$ be the largest cost of any single chore to any agent. A total subsidy of at most $d/24$ suffices to bring each agent’s net cost to at most her maximin share (MMS), and this bound is sharp.

即使至多一人可以领取正补贴，最坏情形下的最小总补贴仍为 $d/24$。领取者可根据实例选择。<br>
Even when at most one agent may receive a positive subsidy, the worst-case minimum total subsidy is still $d/24$. The recipient may be chosen for each instance.

[证明](PROOF.md)给出实数成本下的上界，并给出一个在两种补贴要求下都达到该界的[九件实例](examples/nine_chores.json)。<br>
The [proof](PROOF.md) establishes the bound for real-valued costs and gives a single [nine-chore instance](examples/nine_chores.json) that attains it under both objectives.

复验<br>
Verification
------------

在仓库根目录使用 Python 3.11 或更高版本运行以下命令。只需 Python 标准库。<br>
From the repository root, run the following command with Python 3.11 or later. Only the standard library is required.

~~~sh
python verify_nine_chores.py
~~~

[核验程序](verify_nine_chores.py)重建将九件不同任务分成三个包的全部 3,281 种方式（包不计顺序，允许空包），并检查[有理数证书](certificates/nine_chores.json)覆盖的全部 2,457 个根情形。它另行枚举达到例的全部 19,683 种分配。<br>
The [verifier](verify_nine_chores.py) reconstructs all 3,281 unordered partitions of the nine distinct chores into three possibly empty bundles and checks all 2,457 root cases covered by the [rational certificate](certificates/nine_chores.json). It separately enumerates all 19,683 allocations of the attaining instance.

成功时退出码为 0，输出 JSON 中的 `upper_bound`、`example.value.sigma` 和 `example.value.sigma_1` 均为 `"1/24"`。<br>
On success, the verifier exits with code 0 and reports `"1/24"` for `upper_bound`, `example.value.sigma`, and `example.value.sigma_1` in the JSON output.

与已有工作的关系<br>
Relation to prior work
----------------------

对于三名参与者，在 $d=1$ 的归一化下，Wu、Xue 和 Zhou 给出了适用于任意任务件数的总补贴上界 $1/6$，并给出了一个需要总补贴 $2/49$ 的九件实例。本文确定了九件任务的精确最坏值，两种补贴要求下均为 $1/24$。[IJCAI 2025 论文](https://ijcai.org/proceedings/2025/454)<br>
For three agents with $d=1$, Wu, Xue, and Zhou proved an upper bound of $1/6$ on the total subsidy for any number of chores and gave a nine-chore instance requiring a total subsidy of $2/49$. For nine chores, we determine the exact worst-case value to be $1/24$ under both objectives. [IJCAI 2025 paper](https://ijcai.org/proceedings/2025/454)
