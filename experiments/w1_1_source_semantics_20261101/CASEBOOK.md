# W1.1：规范命题与全部页面语义

原W1保留；本版是开发性表示审计。五种语义标签与不可观测分开。所有人工签核待完成、Y未观测。
精确短引文只保存在 drafts/ 对应语句记录；statement_index.json 提供指针及已核对的证据哈希。

## W1-01 · 原索引 127

All regular Indian Railways trains cancelled till 30th September, 2020.

参考标签：Refuted；规范化状态：PARTIAL_SCOPE。
实体：Indian Railways regular passenger train services；关系：all regular services cancelled until；值：2020-09-30。
事件时间：{"as_of": "2020-08-10", "end": "2020-09-30", "start": null}；地点：India；单位：calendar date。
限定：all regular trains; distinguish special trains；announcement of cancellation versus actual service operation。
The scope of regular services and start of cancellation interval are not established from accessible reference evidence.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P001 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P002 | UNOBSERVED | NON_URL_METADATA_SENTINEL | NOT_EVALUABLE | 无可检查语句 |

## W1-02 · 原索引 180

In Kenya now with a population of about 48 million, we have one judge serving over 300,000 people

参考标签：Supported；规范化状态：CONTEXT_QUALIFIED。
实体：Kenya judiciary and national population；关系：population per judge exceeds；值：300000。
事件时间：{"as_of": "2020-08-01", "population_measurement_year": 2019, "judge_count_report_period": "2017/18"}；地点：Kenya；单位：people per judge。
限定：population approximately 48 million；judge count excludes magistrates unless reference states otherwise；population and judge-count years differ。
Ratio 47.6m/155 is reproducible only from dataset numbers; neither source value is independently checked.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P003 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P004 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P005 | UNOBSERVED | NOT_FOUND | NOT_EVALUABLE | 无可检查语句 |
| P006 | UNOBSERVED | ARCHIVE_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P007 | NOT_ADDRESSED | BODY_READABLE | NO_RELEVANT_PROPOSITION | 无可检查语句 |
| P008 | UNOBSERVED | ARCHIVE_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |

## W1-03 · 原索引 463

Cloth masks do not filter anything.

参考标签：Refuted；规范化状态：EXPLICIT_WITH_UNSPECIFIED_PHYSICAL_SCOPE。
实体：cloth face masks；关系：filter no particles or droplets at all；值：universal negative。
事件时间：{"as_of": "2020-06-21", "applicability_interval": null}；地点：not specified by proposition; US is dataset context；单位：qualitative filtration。
限定：do not substitute clinical infection reduction for zero filtration；universal claim, not equality with respirators。
Filter anything is universal and underspecified in particle size; preserve that wording.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P009 | UNOBSERVED | BLOCKED_CHALLENGE | NOT_EVALUABLE | 无可检查语句 |
| P010 | ASSERT_REFUTE | BODY_READABLE | FULL | P010-S1, P010-S2, P010-S3 |
| P011 | UNOBSERVED | REDIRECT_THEN_BLOCKED | NOT_EVALUABLE | 无可检查语句 |
| P012 | UNOBSERVED | ARCHIVE_AND_CURRENT_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P013 | UNOBSERVED | ARCHIVE_AND_CURRENT_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |

## W1-04 · 原索引 584

Thyrocare labs are sealed in Thane over false-positive COVID-19 testing.

参考标签：Refuted；规范化状态：CONTEXT_QUALIFIED。
实体：Thyrocare laboratory facilities in Thane；关系：sealed because of false-positive COVID-19 testing；值：physical closure plus asserted cause。
事件时间：{"as_of": "2020-06-07", "closure_event_time": null}；地点：Thane, India；单位：binary event with causal qualifier。
限定：stopping COVID testing is not closing the entire laboratory；do not infer later closure from earlier testing suspension。
Exact facility and closure-event date remain unspecified.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P014 | UNOBSERVED；元数据：ASSERT_SUPPORT | METADATA_ONLY | NOT_EVALUABLE | P014-S1 |
| P015 | UNOBSERVED | ARCHIVE_LOGIN_TARGET_MISMATCH | NOT_EVALUABLE | 无可检查语句 |
| P016 | ASSERT_REFUTE | BODY_READABLE | FULL | P016-S1, P016-S2, P016-S3 |
| P017 | UNOBSERVED | LOGIN_GATE_NOT_SPECIFIC_TWEET | NOT_EVALUABLE | 无可检查语句 |
| P018 | UNOBSERVED | ARCHIVE_LOGIN_TARGET_MISMATCH | NOT_EVALUABLE | 无可检查语句 |
| P019 | NOT_ADDRESSED | BODY_READABLE | PARTIAL | P019-S1, P019-S2, P019-S3 |
| P020 | UNOBSERVED | ARCHIVE_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |

## W1-05 · 原索引 678

Since the week ending March 14, Wisconsin actually saw a drop in tourism spending compared to last year of $1.7 billion.

参考标签：Supported；规范化状态：CONTEXT_QUALIFIED。
实体：Wisconsin tourism spending；关系：cumulative year-over-year decline since week ending March 14；值：approximately 1.7 billion。
事件时间：{"start_week_ending": "2020-03-14", "claim_as_of": "2020-05-24", "reference_latest_week_ending": "2020-05-16"}；地点：Wisconsin, United States；单位：USD。
限定：cumulative loss versus same period previous year；1.7B claim is rounded; reference reports 1.775B；do not substitute full-calendar-year 2020 loss。
Year and end of comparison window come from claim date / reference, not explicit in literal statement; retain this interpretive step.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P021 | ATTRIBUTED_ONLY | BODY_READABLE | CONTEXT_QUALIFIED | P021-S1, P021-S2 |
| P022 | ASSERT_SUPPORT | BODY_READABLE | CONTEXT_QUALIFIED | P022-S1, P022-S2 |
| P023 | NOT_ADDRESSED | BODY_READABLE | MISMATCH | P023-S1 |
| P024 | UNOBSERVED | ARCHIVE_UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |

## W1-06 · 原索引 1047

F. Scott Fitzgerald wrote a letter in the 1920 Spanish Influenza pandemic, in which he wrote to someone named “Rosemary” in which he wrote: “Even the bars, as I told Hemingway, but to that he punched me in the stomach, to which I asked if he had washed his hands,” the alleged letter says. “He hadn’t. He is much the denier, that one. Why, he considers the virus to be just influenza.”

参考标签：Refuted；规范化状态：EXPLICIT_ATTRIBUTION。
实体：the circulated letter to Rosemary containing the quoted bar/Hemingway passage；关系：was authored by F. Scott Fitzgerald during Spanish influenza；值：F. Scott Fitzgerald; alleged 1920。
事件时间：{"alleged_letter_year": 1920, "circulation_as_of": "2020-03-19", "observed_primary_publication_date": "2020-03-13"}；地点：alleged letter: South of France; publication/circulation context US；单位：author identity and year。
限定：authorship target, not accuracy of fictional events；actual author statement and satire disclaimer belong to page context。
Reference is corroborated by first-party byline/disclaimer; no independent human adjudication.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P025 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P026 | ASSERT_REFUTE | BODY_READABLE | FULL | P026-S1, P026-S2, P026-S3 |
| P027 | NOT_ADDRESSED | BODY_READABLE | NO_RELEVANT_PROPOSITION | 无可检查语句 |
| P028 | ASSERT_REFUTE | BODY_READABLE | FULL | P028-S1, P028-S2, P028-S3 |

## W1-07 · 原索引 1238

A doctor's office in New South Wales was visited by people who had been exposed to the coronavirus.

参考标签：Supported；规范化状态：UNRESOLVED_SCOPE。
实体：one doctor office in New South Wales；关系：was visited by multiple people exposed to coronavirus；值：existential office with plural visitors。
事件时间：{"as_of": "2020-02-14", "event_time": null}；地点：New South Wales, Australia；单位：['one office', 'multiple exposed people']。
限定：do not replace one office with separate GPs；do not replace NSW with Melbourne/Victoria；original specific Aberglasslyn allegation is a different scoped proposition。
Neither different GP visits nor a hoax concerning one town resolves the literal broad singular-office/plural-visitors claim.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P029 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P030 | NOT_ADDRESSED | READABLE_CURRENT | DIFFERENT_SCOPED_PROPOSITION | 07-P030-S1, 07-P030-S2, 07-P030-S3 |
| P031 | NOT_ADDRESSED | READABLE_CURRENT | PARTIAL_AND_MISMATCH | 07-P031-S1, 07-P031-S2 |
| P032 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P033 | NOT_ADDRESSED | READABLE_CURRENT | PARTIAL | 07-P033-S1, 07-P033-S2 |

## W1-08 · 原索引 1429

Donald Trump is rated international public opinion polls below Xi Jinping.

参考标签：Supported；规范化状态：CONTEXT_QUALIFIED。
实体：Donald Trump and Xi Jinping；关系：international public-opinion rating of Trump lower than Xi；值：Trump < Xi。
事件时间：{"as_of": "2019-12-19", "contextual_survey_year": 2018}；地点：international; contextual survey covers 25 countries；单位：country-median confidence in handling world affairs (contextual)。
限定：specific poll scope, not all international polls；not preference for US versus China as global leading power。
Poll instrument, country aggregation and year are supplied by reference context, not all present in literal claim.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P034 | ATTRIBUTED_ONLY | READABLE_CURRENT | CONTEXT_QUALIFIED | 08-P034-S1 |
| P035 | ASSERT_SUPPORT | READABLE_CURRENT | CONTEXT_QUALIFIED | 08-P035-S1, 08-P035-S2 |
| P036 | NOT_ADDRESSED | READABLE_CURRENT | NO_RELEVANT_PROPOSITION | 无可检查语句 |

## W1-09 · 原索引 1460

A female army sergeant who became a hero for her war-time actions is the first woman to earn a Silver Star since WWII.

参考标签：Supported；规范化状态：CONTEXT_QUALIFIED。
实体：Leigh Ann Hester (identity supplied by reference)；关系：was the first woman awarded a Silver Star since WWII；值：first, not only。
事件时间：{"award_date_contextual": "2005-06-16", "action_date_contextual": "2005-03-20", "claim_as_of": "2019-12-09", "later_award_contextual": "2008-03-21"}；地点：US military; wartime action in Iraq；单位：historical ordering of awards。
限定：being first does not mean being sole recipient since WWII；do not portray old award as newly awarded in 2019。
Reference identifies the person; original full page is inaccessible.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P002 | UNOBSERVED | NON_URL_SENTINEL | NOT_EVALUABLE | 无可检查语句 |
| P037 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P038 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P039 | ASSERT_SUPPORT | READABLE_CURRENT | CONTEXT_QUALIFIED | 09-P039-S1, 09-P039-S2 |

## W1-10 · 原索引 2137

“America is like a healthy body and its resistance is threefold: its patriotism, its morality and its spiritual life. If we can undermine these three areas, America will collapse from within.

参考标签：Refuted；规范化状态：MISSING_PREDICATE。
实体：None；关系：attribution predicate missing from literal claim；值：quoted geopolitical prescription。
事件时间：{"claim_as_of": "2019-05-30", "alleged_utterance_date": null}；地点：America as object of quotation; alleged speaker location unknown；单位：not applicable。
限定：literal claim omits speaker and asserted attribution；Stalin attribution appears only in QA/justification。
Do not silently change the test item to Stalin said X; that is a separate contextual interpretation.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P002 | UNOBSERVED | NON_URL_SENTINEL | NOT_EVALUABLE | 无可检查语句 |
| P040 | UNOBSERVED | HEADER_ONLY_BODY_UNAVAILABLE | NOT_EVALUABLE | 10-P040-M1 |
| P041 | NOT_ADDRESSED | READABLE_CURRENT | NO_RELEVANT_PROPOSITION | 无可检查语句 |

## W1-11 · 原索引 2521

Blake Griffin, a forward for the Detroit Pistons basketball team, will pay $258,000 per month in child support to his ex Brynn Cameron.

参考标签：Refuted；规范化状态：UNRESOLVED_TIME_AND_MODALITY。
实体：Blake Griffin and Brynn Cameron；关系：Griffin will pay Cameron child support of；值：258000。
事件时间：{"claim_as_of": "2019-02-25", "order_period": null, "related_reports_dated": "2018-08", "reference_evaluation_date": "2020-08-03"}；地点：Los Angeles, California, United States (contextual court jurisdiction)；单位：USD per month。
限定：amount unknown/confidential in inspected reference；report of denial is not verification of negation；distinguish ordered versus actual paid amount and time。
Future will pay, reported order, and actual payments are not interchangeable; original underlying court record absent.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P042 | MIXED | READABLE_CURRENT | PARTIAL_MODALITY_AND_TIME_UNRESOLVED | 11-P042-S1, 11-P042-S2 |
| P043 | ASSERT_REFUTE | READABLE_CURRENT | PARTIAL_MODALITY_AND_TIME_UNRESOLVED | 11-P043-S1, 11-P043-S2, 11-P043-S3 |
| P044 | NOT_ADDRESSED | READABLE_CURRENT | DIFFERENT_PROPOSITION | 11-P044-S1 |
| P045 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P046 | MIXED | READABLE_CURRENT | PARTIAL_MODALITY_AND_TIME_UNRESOLVED | 11-P046-S1, 11-P046-S2, 11-P046-S3 |
| P047 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P048 | MIXED | READABLE_CURRENT | PARTIAL_MODALITY_AND_TIME_UNRESOLVED | 11-P048-S1, 11-P048-S2 |
| P049 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |

## W1-12 · 原索引 2772

South Africa has invested more than R2 trillion in infrastructure projects over the past 10 years to build more schools, clinics, roads and the freight logistics network.

参考标签：Supported；规范化状态：UNRESOLVED_INTERVAL。
实体：South African public sector；关系：invested more than 2 trillion in infrastructure over prior ten years；值：> 2 trillion。
事件时间：{"claim_as_of": "2019-01-12", "ten_year_window_start": null, "ten_year_window_end": null, "exact_financial_years": null}；地点：South Africa；单位：ZAR。
限定：schools, clinics, roads, freight logistics included；actual spending versus plans；financial versus calendar years unresolved；1998/99-2016/17 aggregate is not the same interval。
Dataset says 2.3T; reference unavailable and amount QA uses Metadata; annex only supports related definitions and other periods.

| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |
|---|---|---|---|---|
| P002 | UNOBSERVED | NON_URL_SENTINEL | NOT_EVALUABLE | 无可检查语句 |
| P050 | UNOBSERVED | UNAVAILABLE | NOT_EVALUABLE | 无可检查语句 |
| P051 | NOT_ADDRESSED | READABLE_CURRENT | MISMATCH | 12-P051-S1, 12-P051-S2 |

