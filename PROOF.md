# A sharp subsidy bound for nine chores

Let $c_i$ be agent $i$’s nonnegative additive cost function on a set $M$ of nine indivisible chores, for $i\in\{1,2,3\}$. Write $c_i(e)=c_i(\{e\})$. Her maximin share (MMS) $\mu_i$ is the minimum, over partitions of $M$ into three bundles, of the largest bundle cost under $c_i$. Empty bundles are allowed. An allocation $X=(X_1,X_2,X_3)$ assigns bundle $X_i$ of such a partition to agent $i$. The least subsidy she needs is $[c_i(X_i)-\mu_i]_+$, where $[t]_+=\max(t,0)$. Let $\sigma$ be the minimum total subsidy over all allocations and $\sigma_1$ the minimum when at most one agent receives a positive subsidy. The recipient may depend on the instance. All costs and subsidies share a common unit.

**Theorem.** For three agents and nine chores, $\sigma\leq\sigma_1\leq d/24$, where $d=\max_{i,e}c_i(e)$. There is an instance with $d=1$ for which $\sigma=\sigma_1=1/24$.

## Reduction to finitely many cases

When $d=0$, every allocation requires zero subsidy. Otherwise, divide all costs by the same $d$ and sort each agent’s row in nonincreasing order, with rank 1 the most costly. Sorting preserves each agent’s MMS. For any allocation of the ranks, process ranks 9 through 1 and give the agent assigned rank $j$ her cheapest remaining original chore. At that step $j$ chores remain, and at most $j-1$ original chores cost her strictly more than her $j$-th largest cost. Her chosen chore therefore costs at most that amount, including when costs are tied. No agent’s bundle cost increases under this map, so no subsidy increases and no new recipient is needed. Taking the minima shows that $\sigma$ and $\sigma_1$ for the original normalized instance are each at most their respective values in the sorted instance. Scaling back multiplies subsidies by $d$.

Call a bundle *acceptable* to agent $i$ if its cost to her is at most $\mu_i$, and *rejected* otherwise. Wu, Xue, and Zhou (2025, Definition 2.5) call an acceptable bundle *MMS-feasible*. Write $A\preceq B$ if $A$ contains at most as many ranks as $B$ in every prefix $\{1,\dots,k\}$. Matching ranks in increasing order gives $c_i(A)\leq c_i(B)$ for every nonincreasing nonnegative cost row. Removing the common ranks preserves the prefix inequalities, so each element of $A\setminus B$ can likewise be matched to a distinct element of $B\setminus A$ of at least the same cost.

Suppose two agents have MMS partitions $P,Q$ with $A\in P$, $B\in Q$ and $A\preceq B$. The owner of $P$ splits $M\setminus B$ into two bundles she accepts by removing $B\setminus A$ from her other two bundles and reinserting $A\setminus B$ at the matched positions. If the third agent accepts $B$, give it to her and let the owner of $Q$ choose her cheaper bundle from this split. Her cost for the remainder is at most twice her MMS because it is the union of the other two bundles of $Q$. Otherwise give $B$ to the owner of $Q$ and let the third agent choose her cheaper bundle from the same split. Her cost for the remainder is strictly less than twice her MMS because $c_i(M)\leq3\mu_i$ and she rejected $B$. The chooser and the owner of $P$, who gets the last bundle, are both within their MMS, so the allocation requires zero subsidy.

The graph has one vertex for each unordered partition of the nine ranks into three possibly empty bundles. Join two partitions when no pair of their bundles is comparable. If $\sigma_1>0$, any choice of one MMS partition per agent gives a triangle. The graph has 3,281 vertices, 1,130 edges and 91 triangles. In any agent’s MMS partition, each of the other two agents accepts at least one bundle by averaging. If they can choose distinct acceptable bundles, the partitioner takes the remaining bundle and all three are within their MMS. Otherwise each accepts only the same bundle, as in Wu, Xue, and Zhou (2025, Section 3.1). Relabel the agents to match the triangle vertices and choose the shared acceptable bundle in each partition, giving $91\cdot3^3=2{,}457$ root cases.

## The certificate for the upper bound

Suppose for contradiction that the sorted, normalized instance has $\tau=\sigma_1>q$, where $q=1/24$. In each root case, costs are between zero and one and nonincreasing in rank. Each agent’s MMS bundles and the designated shared bundles of the other two partitions cost her at most her MMS. The following allocations give two further families of inequalities. When only one agent can require a subsidy, $\tau>0$ forces that agent’s excess to be positive, so the positive part can be dropped.

- If agent $i$ takes a rejected bundle $B$ from another agent’s MMS partition, the third agent can take the shared acceptable bundle and the partitioner can take the remaining bundle. Hence $c_i(B)-\mu_i\geq\tau$.
- In any complete allocation $X$ in which the other two agents receive bundles dominated by known acceptable bundles under $\preceq$, agent $i$’s excess satisfies $c_i(X_i)-\mu_i\geq\tau$.

The [verifier](verify_nine_chores.py) reconstructs these inequalities from the bundle and agent labels in the [rational certificate](certificates/nine_chores.json). In 2,442 roots, a nonnegative rational combination proves $\tau\leq q$ directly. In ten roots, the combination also uses $\tau\geq q$, which follows from the contradiction assumption. For each of those roots the certificate bounds the three excesses of a fixed allocation. Two are at most zero and the remaining one is at most $q$, so the allocation contradicts $\tau>q$.

The remaining five roots use case-splitting trees. At each split, the certificate specifies a complete allocation. If at most one excess is positive, choose the allowed recipient. The other two excesses are at most zero, and $\tau>0$ forces the recipient’s excess to be at least $\tau$. If at least two excesses are positive, choose a pair with strictly positive excesses. There are three choices in each case, covering every possible sign pattern, including zeros, under the contradiction assumption. An allocation with all excesses nonpositive would itself give $\tau=0$.

Along a root-to-leaf path consistent with a counterexample, let $\delta$ be the minimum of $\tau-q$ and the excesses required to be strictly positive on that path. The minimum is positive. At each leaf a nonnegative rational combination of the applicable inequalities gives $\delta\leq0$. The five trees have 38 splits and 195 leaves. The verifier checks root coverage, every branch and its path, and the positivity of the stored weights, every variable coefficient and the right-hand side in each combination. Nonnegative rational combinations preserve inequalities over the reals, so $\sigma_1\leq q$ for every normalized instance. Also $\sigma\leq\sigma_1$, since the former minimum allows every allocation admitted by the latter.

## An attaining instance

In the [attaining instance](examples/nine_chores.json), the cost matrix is

$$
C=\frac1{24}\begin{pmatrix}
8&21&17&23&14&9&16&12&18\\
8&21&18&23&14&10&15&11&18\\
8&21&17&24&14&8&14&11&18
\end{pmatrix}.
$$

The first two numerator rows are the costs of agents $R$ and $C$ in Wu, Xue, and Zhou’s example (IJCAI 2025, Section 3.4), which uses the row and column partitions of Feige, Sapir, and Tauber (WINE 2021). Wu, Xue, and Zhou’s unscaled instance has a maximum chore cost of $24.5$ in the $U$ row and a minimum total subsidy of $1$, yielding $2/49$ after common normalization. Replacing the $U$ row lowers the largest unscaled chore cost to $24$ and keeps the minimum total subsidy at $1$. The matrix above divides all three resulting rows by $24$ to give $d=1$. [Wu, Xue, and Zhou](https://ijcai.org/proceedings/2025/454) · [Feige, Sapir, and Tauber, arXiv v2](https://arxiv.org/abs/2104.04977v2) · [WINE 2021 proceedings](https://doi.org/10.1007/978-3-030-94676-0_20)

The MMS values are $(46,46,45)/24$. Number the original chores $1,\dots,9$ by the columns of $C$. Assigning $\{1,2,3\}$, $\{4,6,8\}$ and $\{5,7,9\}$ to agents 1, 2 and 3 gives costs $(46,44,46)/24$, so only agent 3 needs a subsidy, of $1/24$. The verifier computes the MMS values over all unordered three-bundle partitions and evaluates all $3^9=19{,}683$ labeled allocations. Both minima are $1/24$, with 42 attaining allocations for each objective.
