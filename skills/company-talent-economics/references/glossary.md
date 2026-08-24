# Glossary and terminology discipline

Use these terms exactly. Imprecise wording is treated as an error in review.

**In every language.** The table below is English/Chinese because those are the two languages the
distinctions were first written in, but the discipline is language-independent: whatever language you
write in, use that language's *accounting and corporate-law* term, not its colloquial one. The traps
recur everywhere — a company's constitutional document is its articles (章程 / Satzung / statuts /
定款 / 정관 / устав), never a "constitution"; employer benefit expense is not take-home pay
(Personalaufwand ≠ Nettogehalt, 人件費 ≠ 手取り); a grant is not a vest (授出 ≠ 归属, Zuteilung ≠
Unverfallbarkeit, 付与 ≠ 権利確定); observed transition shares are not promotion probabilities.

Locale packs carry the display labels for the five claim types, and `forbidden_terms` in a pack lists
the traps `validate_bundle.py` checks mechanically for that language. Add your language's traps there
when you add a pack — a mechanical check beats a good intention.

| Term (EN) | 中文 | Definition | Do not confuse with |
|---|---|---|---|
| articles / charter | 公司章程（组织章程大纲及细则） | The registered constitutional document of the legal entity | 「宪法」(a state constitution; never use for a company) |
| shareholders' agreement | 股东协议 / 投资协议 | Private contract among shareholders; may grant rights not in the articles | 章程 |
| WVR / dual-class | 不同投票权 / AB 股 | Share classes with unequal votes per share | 优先股 (preferred stock: economic preference, not necessarily votes) |
| economic ownership | 经济权益 | Share of cash-flow rights | 投票权 |
| voting power | 投票权 | Share of votes | 经济权益 |
| total compensation (TC) | 总薪酬 | base + expected cash bonus/commission + annualised vested equity value, pre-tax | 「年薪」(often means base only), 「总包」(colloquial, ambiguous) |
| cash TC | 现金总薪酬 | TC excluding equity | |
| base salary | 基本薪资 | Fixed cash | 「工资」(ambiguous) |
| annualised equity | 年化归属股份价值 | value of shares expected to vest per year, at a stated price basis | grant-date total value (授予日总值) |
| employee benefit expense | 雇员福利开支 | IFRS/PRC GAAP line: wages, bonuses, social insurance, housing fund, SBC, welfare | cash paid to employees (支付给职工的现金, cash-flow statement, excludes SBC) |
| share-based compensation (SBC) | 以股份为基础的薪酬 / 股份支付 | Accounting expense of equity awards over vesting | grant value; realised employee value |
| grant | 授出 / 授予 | Award is made | vest 归属 (award becomes unconditional) |
| share award / RSU | 奖励股份 / 受限制股份单位 | Full-value award | option 购股权 / 期权 (right to buy at strike) |
| dilution | 摊薄 | Reduction in per-share economic/voting interest from new issuance | 稀释 (acceptable synonym; be consistent) |
| headcount | 全职雇员数 | Employees on payroll at a date | 用工总数 incl. outsourced/dispatch (外包/劳务派遣) |
| R&D personnel | 研发人员 | As defined by the issuer, usually by function not degree | engineers by title |
| profit pool | 利润池 | Segment/product gross or operating profit where value is captured | revenue 收入 |
| observed_fact | 披露事实 | Stated in a Tier A/B document | 观察 (vague) |
| derived_metric | 派生指标 | Arithmetic on disclosed facts | |
| assumption | 模型假设 | Chosen by analyst, stated with range | |
| inference | 推断 | Model output or judgement | |
| reconstruction | 重建 | Charter/governance terms rebuilt from secondary documents | 原文 |
| observed transition share | 观察到的转换份额 | share of public-profile transitions from a state | promotion probability 晋升概率 (needs true denominator) |
| market replacement band | 市场替代区间 | external hire/retain cost | |
| economic justification band | 经济合理区间 | affordability from profit pool and value-at-risk | |
| internal-equity band | 内部公平区间 | implied by adjacent roles and plans | |
| defensible zone | 可辩护区间 | overlap of the three bands | recommendation 建议薪酬 (only if user asks) |

Currency: always state currency and whether HKD/USD figures were converted, with the rate and date. Fiscal year: state FY end; do not mix calendar and fiscal years.
