# W1：12 条声明 × 全部指定页面审计

全部为 AI 辅助暂定标注；人工签核 0，Y 未采集。θ 是数据集参考标签。
`V_current` 仅指本轮取得的非归档 URL 表示，可能来自浏览器缓存；不保证实时性。历史 V 一律 UNKNOWN。
候选表示可供 W2 人工审阅，未授权 W3。页号 Pxxx 保留原 URL；归档与非归档表示不能互相代替。

## W1-01 · train[127]

All regular Indian Railways trains cancelled till 30th September, 2020.

参考 θ=0 (Refuted); 声明日期字段：10-8-2020。
参考核验：数据集声称截至 2020-08-10 铁道部没有新发延长停运通知；参考页无法访问，未独立核验这一时间限定。不能由无新通知推出所有列车实际运营。
处置：隔离。仅一个不可读参考页及 Metadata 非 URL 占位，没有可审阅非参考页面。

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P001](https://web.archive.org/web/20210721115102/https://newsmobile.in/articles/2020/08/11/fact-check-all-regular-trains-cancelled-till-30th-september-heres-the-truth/) | reference | UNKNOWN | UNKNOWN / 未观测 | UNAVAILABLE; access_log.jsonl:P001; browser_01_04/P001.json |
| P002 Metadata | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | NON_URL_METADATA_SENTINEL; url_inventory.json:P002; access_log.jsonl:P002 |

## W1-02 · train[180]

In Kenya now with a population of about 48 million, we have one judge serving over 300,000 people

参考 θ=1 (Supported); 声明日期字段：1-8-2020。
参考核验：数据集以 2019 人口 47.6 million 与 2017/18 司法报告 155 judges 计算每名法官约 307096.77 人；算术可复算，但原网页均未核验，两个年份与 2020 年声明时点不相同，不能升级为独立真值。
处置：隔离。人口/司法原文不可读；Symbolab 首页不保存参数、运算结果或肯尼亚事实。

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P003](https://web.archive.org/web/20210127231105/https://africacheck.org/fact-checks/reports/factchecking-kenyas-chief-justice-judiciary-funding-and-backlog-cases) | reference | UNKNOWN | UNKNOWN / 未观测 | UNAVAILABLE_REFERENCE; access_log.jsonl:P003; browser_01_04/P003.json |
| [P004](https://web.archive.org/web/20210105192026/https://www.knbs.or.ke/?p=5621) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | UNAVAILABLE; access_log.jsonl:P004; browser_01_04/P004.json |
| [P005](https://www.judiciary.go.ke/wp-content/uploads/sojar20172018.pdf) | evidence | UNKNOWN | UNKNOWN / 未观测 | NOT_FOUND; access_log.jsonl:P005; texts/P005.txt; browser_01_04/P005.json |
| [P006](https://web.archive.org/web/20230420135104/https://www.judiciary.go.ke/wp-content/uploads/sojar20172018.pdf) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_UNAVAILABLE; access_log.jsonl:P006; browser_01_04/P005.json |
| [P007](https://www.symbolab.com/) | evidence | UNKNOWN | UNKNOWN / 未观测 | IRRELEVANT_GENERIC_CALCULATOR; texts/P007.txt:L1-L29; access_log.jsonl:P007 |
| [P008](https://web.archive.org/web/20230420025754/https://www.symbolab.com/) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_UNAVAILABLE; access_log.jsonl:P008; texts/P007.txt |

## W1-03 · train[463]

Cloth masks do not filter anything.

参考 θ=0 (Refuted); 声明日期字段：21-6-2020。
参考核验：AFP 当前文章明确否定 cloth masks do not filter anything；其 2020 年文章援引专家与动物实验。这里只核验该参考文章表达的结论，未独立阅读被引用论文/政府页面或原始 Facebook 内容。
处置：隔离。仅事实核查参考页有可读完整立场。原始帖及非参考证据未取得可标注内容，不能将参考页引述的错误帖子视为独立原网页。

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P009](https://perma.cc/L98Y-GG8N) | original, original_archive | UNKNOWN | UNKNOWN / 未观测 | BLOCKED_CHALLENGE; access_log.jsonl:P009; texts/P009.txt:L1; browser_01_04/P009.json |
| [P010](https://web.archive.org/web/20210222141326/https://factcheck.afp.com/covid-19-cases-spike-us-mask-misinformation-also-spreads) | reference | 0 | UNKNOWN / 未观测 | REFERENCE_ONLY_CURRENT_STANCE; browser_01_04/P010.json:L24-L25,L67-L72 |
| [P011](https://www.dhs.wisconsin.gov/covid-19/mask.htm) | evidence | UNKNOWN | UNKNOWN / 未观测 | REDIRECT_THEN_BLOCKED; access_log.jsonl:P011; texts/P011.txt:L1-L5; browser_01_04/P011.json |
| [P012](https://web.archive.org/web/20230318014229/https://dhs.wisconsin.gov/covid-19/mask.htm) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_AND_CURRENT_UNAVAILABLE; access_log.jsonl:P012; browser_01_04/P012.json |
| [P013](https://web.archive.org/web/20201221234605/https://www.biorxiv.org/content/10.1101/2020.04.06.028688v1) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_AND_CURRENT_UNAVAILABLE; access_log.jsonl:P013; browser_01_04/P013.json |

## W1-04 · train[584]

Thyrocare labs are sealed in Thane over false-positive COVID-19 testing.

参考 θ=0 (Refuted); 声明日期字段：7-6-2020。
参考核验：Vishvas 当前参考文章区分停止 COVID 检测与封闭实验室，并给出否定结论及采访。Mumbai Mirror 原报道只确认暂停检测；该文没有明确否定之后实验室封闭，不能独立确定整条声明真假。required_reannotation=true 保留。
处置：隔离。原 Facebook 只有 HTML 元数据明确断言完整错误声明，未取得可读正文或历史版本；严格正文候选为零，另列人工复核线索。

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P014](https://www.facebook.com/manojkalwar/posts/10220950134676330) | original | 1 (仅元数据) | UNKNOWN / 未观测 | METADATA_ONLY_LEAD; snapshots/P014.html:meta[property='og:description']@content; browser_01_04/P014_metadata_inspection.json; texts/P014.txt:L1; browser_01_04/P014.json |
| [P015](https://web.archive.org/web/20230510143422/https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2Fmanojkalwar%2Fposts%2F10220950134676330) | original_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_LOGIN_TARGET_MISMATCH; url_inventory.json:P015; access_log.jsonl:P015; browser_01_04/P015.json |
| [P016](https://web.archive.org/web/20200817190134/https://www.vishvasnews.com/english/viral/fact-check-no-this-thane-lab-is-not-sealed-over-false-positive-covid19-testing/) | reference | 0 | UNKNOWN / 未观测 | REFERENCE_ONLY_CURRENT_STANCE; browser_01_04/P016.json:L51-L60,L68-L80,L91-L94 |
| [P017](https://twitter.com/hashtag/ThyrocareLab?src=hashtag_click) | evidence | UNKNOWN | UNKNOWN / 未观测 | AGGREGATE_PAGE_LOGIN_GATE; access_log.jsonl:P017; texts/P017.txt:L1; browser_01_04/P017.json |
| [P018](https://web.archive.org/web/20230510140151/https://twitter.com/login) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_LOGIN_TARGET_MISMATCH; url_inventory.json:P018; access_log.jsonl:P018; browser_01_04/P018.json |
| [P019](https://mumbaimirror.indiatimes.com/coronavirus/news/tmc-halts-thyrocare-covid-19-testing-in-thane/articleshow/75903033.cms) | evidence | UNKNOWN | UNKNOWN / 未观测 | PARTIAL_DIFFERENT_PREDICATE; texts/P019.txt:L41-L53; access_log.jsonl:P019 |
| [P020](https://web.archive.org/web/20230418204457/https://mumbaimirror.indiatimes.com/coronavirus/news/tmc-halts-thyrocare-covid-19-testing-in-thane/articleshow/75903033.cms) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_UNAVAILABLE; access_log.jsonl:P020; texts/P019.txt:L41-L53 |

## W1-05 · train[678]

Since the week ending March 14, Wisconsin actually saw a drop in tourism spending compared to last year of $1.7 billion.

参考 θ=1 (Supported); 声明日期字段：24-5-2020。
参考核验：PolitiFact affirms the quoted $1.7B claim and reports a $1.775B cumulative year-over-year decline from week ending March 14 through May 16, 2020, based on Tourism Economics studies commissioned by the U.S. Travel Association. The dataset's linked QA evidence page is instead a May 2021 article about the full year 2020. Preserve the stated claim-time scope and rounding; primary study data were not separately fetched.
处置：W2 待人工审阅候选。Provisional current-page candidate only. Human signoff and independent recalculation of the underlying study remain absent; no recovered historical snapshot.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P021](https://web.archive.org/web/20200807031508/https://www.wisn.com/article/upfront-recap-wisconsin-has-lost-dollar17-billion-in-tourism-dollars-since-march-14/32651612) | original, original_archive | 1 | UNKNOWN / 未观测 | CURRENT_SUPPORTS_FULL_CLAIM; browser_05_08/batch_01.json: P021 lines 57-70 |
| [P022](https://web.archive.org/web/20210117152017/https://www.politifact.com/factchecks/2020/jun/12/sara-meaney/yes-state-has-seen-drop-more-billion-tourism-dolla/) | reference | 1 | UNKNOWN / 未观测 | REFERENCE_ONLY_CURRENT_SUPPORTS; browser_05_08/batch_01.json: P022 lines 29-47,87-108 |
| [P023](https://www.wpr.org/wisconsins-tourism-industry-sees-30-percent-spending-decline-2020-due-covid-19) | evidence | UNKNOWN | UNKNOWN / 未观测 | TEMPORAL_AND_SCOPE_MISMATCH; texts/P023.txt lines 38-50; browser_05_08/batch_01.json: P023 lines 36-48 |
| [P024](https://web.archive.org/web/20230515183158/https://www.wpr.org/wisconsins-tourism-industry-sees-30-percent-spending-decline-2020-due-covid-19) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_UNAVAILABLE; access_log.jsonl entry P024; browser_05_08/batch_01.json current counterpart P023 |

## W1-06 · train[1047]

F. Scott Fitzgerald wrote a letter in the 1920 Spanish Influenza pandemic, in which he wrote to someone named “Rosemary” in which he wrote: “Even the bars, as I told Hemingway, but to that he punched me in the stomach, to which I asked if he had washed his hands,” the alleged letter says. “He hadn’t. He is much the denier, that one. Why, he considers the virus to be just influenza.”

参考 θ=0 (Refuted); 声明日期字段：19-3-2020。
参考核验：The reference article identifies a March 2020 parody by Nick Farriella; the nominated McSweeney's current page names him and explicitly denies that Fitzgerald wrote an actual letter. This corroborates the reference label for the attribution claim. The archival timestamp does not establish when the explanatory note was added.
处置：W2 待人工审阅候选。Current-page explicit-refutation candidate. No human signoff and no claim that the correction note existed in the 2020 archived version.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P025](https://web.archive.org/web/20200909222356/https://www.facebook.com/jay.nickeron/posts/2617182365228423) | original, original_archive | UNKNOWN | UNKNOWN / 未观测 | UNAVAILABLE; access_log.jsonl entry P025; browser_05_08/batch_02.json: P025 error |
| [P026](https://web.archive.org/web/20201020164028/https://checkyourfact.com/2020/03/31/fact-check-f-scott-fitzgerald-letter-quarantined-spanish-influenza/) | reference | 0 | UNKNOWN / 未观测 | REFERENCE_ONLY_CURRENT_REFUTES; browser_05_08/batch_02.json: P026 lines 8-20 |
| [P027](https://web.archive.org/web/20201126181530/https://www.altnews.in/) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | IRRELEVANT_CURRENT_HOMEPAGE_ARCHIVE_UNAVAILABLE; browser_05_08/batch_02.json: P027 lines 44-108,360-408 |
| [P028](https://web.archive.org/web/20201020164028/https://www.mcsweeneys.net/articles/this-side-of-paradise-a-letter-from-f-scott-fitzgerald-quarantined-in-the-south-of-france) | evidence, evidence_archive | 0 | UNKNOWN / 未观测 | CURRENT_EXPLICIT_ATTRIBUTION_REFUTATION; browser_05_08/batch_02.json: P028 lines 16-35 |

## W1-07 · train[1238]

A doctor's office in New South Wales was visited by people who had been exposed to the coronavirus.

参考 θ=1 (Supported); 声明日期字段：14-2-2020。
参考核验：AFP evaluates a specific February 14 Aberglasslyn doctor's-office allegation and calls that allegation misleading. The dataset removes the town and changes the target to a broad NSW claim. NSW Health documents two patients separately attending GPs in January, but does not establish the same doctor's office received multiple people. ABC's double-mask GP passage concerns Melbourne/Victoria, not NSW. Do not change the label to Refuted or treat the AFP/Supported discrepancy as natural source disagreement on the same proposition.
处置：隔离。Original specific event, literal broad dataset claim, and cited support do not resolve to one unambiguous full proposition; no determinate nonreference V for the frozen claim.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P029](https://perma.cc/52EG-ER82) | original, original_archive | UNKNOWN | UNKNOWN / 未观测 | UNAVAILABLE; texts/P029.txt line 1; access_log.jsonl P029; browser_05_08/batch_03.json: P029 failure |
| [P030](https://web.archive.org/web/20210126122206/https://factcheck.afp.com/australian-officials-dismiss-hoax-report-coronavirus-exposure-doctors-surgery-new-south-wales-town) | reference | UNKNOWN | UNKNOWN / 未观测 | REFERENCE_PROPOSITION_SCOPE_MISMATCH; browser_05_08/batch_03.json: P030 lines 60-88 |
| [P031](https://www.abc.net.au/news/2020-01-25/first-confirmed-coronavirus-case-australian-as-china-toll-rises/11900428) | evidence | UNKNOWN | UNKNOWN / 未观测 | PARTIAL_AND_GEOGRAPHIC_MISMATCH; texts/P031.txt lines 142-153; browser_05_08/batch_03.json: P031 lines 141-150,175-195 |
| [P032](https://web.archive.org/web/20230316183549/https://www.abc.net.au/news/2020-01-25/first-confirmed-coronavirus-case-australian-as-china-toll-rises/11900428) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | ARCHIVE_UNAVAILABLE; access_log.jsonl entry P032; current counterpart browser_05_08/batch_03.json P031 |
| [P033](https://web.archive.org/web/20210119120854/https://www.health.nsw.gov.au/news/Pages/20200125_03.aspx) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | PARTIAL_SINGULAR_PLURAL_SCOPE_UNRESOLVED; browser_05_08/batch_03.json: P033 lines 45,56-72 |

## W1-08 · train[1429]

Donald Trump is rated international public opinion polls below Xi Jinping.

参考 θ=1 (Supported); 声明日期字段：19-12-2019。
参考核验：FactCheck.org supports the comparison for a 2018 Pew survey of 25 countries, with country-median confidence in world-affairs leadership. It is not a timeless claim about all international polls, every respondent, or preference for U.S. versus China as leading power. The specific primary poll was linked by the reference but not opened because it is outside the frozen nominated-URL set.
处置：隔离。Only a reference article provides determinate full-claim stance; original is a speaker-attributed transcript and nominated QA evidence is a site homepage.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P034](https://www.washingtonpost.com/politics/2019/12/20/transcript-december-democratic-debate/) | original | UNKNOWN | UNKNOWN / 未观测 | QUOTE_ONLY; browser_05_08/batch_04.json: P034 lines 15-18,34-36 |
| [P035](https://web.archive.org/web/20210424230922/https://www.factcheck.org/2019/12/factchecking-the-december-democratic-debate/) | reference | 1 | UNKNOWN / 未观测 | REFERENCE_ONLY_QUALIFIED_CURRENT_SUPPORTS; browser_05_08/batch_04.json: P035 lines 20,65-72 |
| [P036](https://web.archive.org/web/20210424230922/https://www.factcheck.org/) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | IRRELEVANT_CURRENT_HOMEPAGE_ARCHIVE_UNAVAILABLE; browser_05_08/batch_04.json: P036 lines 4-39,65-78 |

## W1-09 · train[1460]

A female army sergeant who became a hero for her war-time actions is the first woman to earn a Silver Star since WWII.

参考 θ=1 (Supported); 声明日期字段：9-12-2019。
参考核验：Lead Stories confirms first recipient since WWII (2005), but warns first does not mean only; later recipient in 2008. Original source unavailable; no military primary record inspected.
处置：隔离。No accessible nonreference source with determinate V.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| P002 Metadata | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | non_url_sentinel; access_log.jsonl:P002 |
| [P037](https://www.theepochtimes.com/female-army-sergeant-repels-ambush-kills-3-becomes-first-woman-to-earn-silver-star-since-wwii_3164385.html) | original | UNKNOWN | UNKNOWN / 未观测 | unavailable; access_log.jsonl:P037 |
| [P038](https://web.archive.org/web/20230602143520/https://www.theepochtimes.com/female-army-sergeant-repels-ambush-kills-3-becomes-first-woman-to-earn-silver-star-since-wwii_3164385.html) | original_archive | UNKNOWN | UNKNOWN / 未观测 | unavailable; access_log.jsonl:P038 |
| [P039](https://web.archive.org/web/20210104203739/https://leadstories.com/hoax-alert/2020/03/Fact-Check-Female-Army-Sergeant-Who-Repelled-Ambush-Was-NOT-Only-Woman-To-Earn-Silver-Star-Since-WWII.html) | reference | 1 | UNKNOWN / 未观测 | reference_current; browser_09_12/references.json; Lead Stories L13-28 |

## W1-10 · train[2137]

“America is like a healthy body and its resistance is threefold: its patriotism, its morality and its spiritual life. If we can undermine these three areas, America will collapse from within.

参考 θ=0 (Refuted); 声明日期字段：30-5-2019。
参考核验：Dataset justification concerns attribution to Stalin, but raw claim omits speaker and attribution; speaker field null. Factcheck current tool extraction only header, and archive search form proves neither attribution nor its absence.
处置：隔离。Incomplete target proposition and no reviewable reference body.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| P002 Metadata | evidence | UNKNOWN | UNKNOWN / 未观测 | non_url_sentinel; access_log.jsonl:P002 |
| [P040](https://web.archive.org/web/20201229200109/https://checkyourfact.com/2019/06/04/fact-check-joseph-stalin-healthy-body-patriotism-morality-spiritual-life-collapse/) | reference | UNKNOWN | UNKNOWN / 未观测 | unavailable_body; browser_09_12/references.json; Check Your Fact L0-20 |
| [P041](https://web.archive.org/web/20210419013822/https://www.marxists.org/reference/archive/stalin/search.htm) | evidence | UNKNOWN | UNKNOWN / 未观测 | irrelevant_search_form; browser_09_12/sources1.json; Stalin Archive L0-13 |

## W1-11 · train[2521]

Blake Griffin, a forward for the Detroit Pistons basketball team, will pay $258,000 per month in child support to his ex Brynn Cameron.

参考 θ=0 (Refuted); 声明日期字段：25-2-2019。
参考核验：PolitiFact refutes the numeric report using the parties joint denial; actual confidential payment amount is unknown. This is a reviewable factcheck reference, not independently verified court truth.
处置：隔离。SI reports the parties denial without independently adjudicating the amount; attributed reports do not determine full-page binary V. No nonreference determinate full-claim body remains.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| [P042](https://web.archive.org/web/20210624155424/https://radaronline.com/videos/kendall-jenner-ex-blake-griffin-ordered-pay-baby-mama-258k-a-month-child-support/) | original, original_archive | UNKNOWN | UNKNOWN / 未观测 | mixed; browser_09_12/sources1.json; Radar L35,74-75 |
| [P043](https://web.archive.org/web/20210624155349/https://www.politifact.com/factchecks/2020/aug/03/viral-image/blake-griffin-and-ex-fiancee-say-he-doesnt-pay-258/) | reference | 0 | UNKNOWN / 未观测 | reference_current; browser_09_12/references.json; PolitiFact L44-59 |
| [P044](https://www.tmz.com/2018/02/14/blake-griffin-dumped-brynn-cameron-wedding-prenup/) | evidence | UNKNOWN | UNKNOWN / 未观测 | partial; browser_09_12/sources2.json; TMZ L76-94 |
| [P045](https://web.archive.org/web/20230607144742/https://www.tmz.com/2018/02/14/blake-griffin-dumped-brynn-cameron-wedding-prenup/) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | unavailable; access_log.jsonl:P045 |
| [P046](https://www.si.com/nba/2018/08/02/blake-griffin-child-support-payments-detroit-pistons-los-angeles-court) | evidence | UNKNOWN | UNKNOWN / 未观测 | attributed_denial; browser_09_12/sources1.json; SI L81-88 |
| [P047](https://web.archive.org/web/20230607144825/https://www.si.com/nba/2018/08/02/blake-griffin-child-support-payments-detroit-pistons-los-angeles-court) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | unavailable; access_log.jsonl:P047 |
| [P048](https://radaronline.com/exclusives/2018/08/kendall-jenner-ex-blake-griffin-ordered-pay-baby-mama-258k-a-month-child-support/) | evidence | UNKNOWN | UNKNOWN / 未观测 | mixed; browser_09_12/sources2.json; Radar L41,79-80 |
| [P049](https://web.archive.org/web/20230607144857/https://radaronline.com/exclusives/2018/08/kendall-jenner-ex-blake-griffin-ordered-pay-baby-mama-258k-a-month-child-support/) | evidence_archive | UNKNOWN | UNKNOWN / 未观测 | unavailable; access_log.jsonl:P049 |

## W1-12 · train[2772]

South Africa has invested more than R2 trillion in infrastructure projects over the past 10 years to build more schools, clinics, roads and the freight logistics network.

参考 θ=1 (Supported); 声明日期字段：12-1-2019。
参考核验：Reference article current fallback 403; dataset numeric answer uses Metadata. Official annex establishes categories and different time totals, not the full claimed ten-year amount.
处置：隔离。Accessible primary PDF only supports a subclaim; reference amount not independently reproduced.

| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |
|---|---|---:|---|---|
| P002 Metadata | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | non_url_sentinel; access_log.jsonl:P002 |
| [P050](https://web.archive.org/web/20210302051737/https://africacheck.org/fact-checks/reports/better-life-all-fact-checking-ancs-2019-election-manifesto) | reference | UNKNOWN | UNKNOWN / 未观测 | unavailable; browser_09_12/references.json; Africa Check error |
| [P051](https://web.archive.org/web/20210413110818/http://www.treasury.gov.za/documents/national%20budget/2018/review/Annexure%20D.pdf#page=1) | evidence, evidence_archive | UNKNOWN | UNKNOWN / 未观测 | partial; browser_09_12/sources2.json; Treasury PDF printed p139 L0-25 |

