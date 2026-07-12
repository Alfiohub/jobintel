# Title Language Filter Report

Input: `data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl`

## Summary
- rows_total: 81911
- rows_with_title: 81911
- rows_en: 81616 (99.64%)
- rows_non_en: 201 (0.25%)
- rows_unknown: 94 (0.11%)

## Policy
- Hints first (`language`/`language_hint` when present)
- Lingua fallback on title text with constrained language set
- with_minimum_relative_distance(0.3)
- minimum confidence threshold: 0.55
- Heuristic non-EN override for strong non-English patterns (e.g. `m-w-d`, German tokens)

## Audit Files
- decisions_csv: `docs/title_language_filter_decisions.csv`
- decisions_jsonl: `docs/title_language_filter_decisions.jsonl`
- Ogni riga contiene bucket, reason e URL annuncio per controllo manuale.

## Top 50 non_en
- 6x Brand Ambassador (Evenementen)
- 3x Business Intelligence Analyst - Hìbrido CDMX
- 3x Técnico en Mantenimiento III
- 2x Lead Recruiter Sales (x/f/m)
- 2x Brand Ambassador (Events)
- 2x KI-Trainer:in & -Consultant (m/w/d)
- 2x Senior Data Scientist
- 2x Initiativbewerbung / Initiative Application - Mediabrands
- 2x Senior Product Owner
- 2x Industrial Engineer Holzbautechnik (m/w/d)
- 2x Senior Architekt (m/w/d)
- 2x Senior Structural Engineer (m/w/d)
- 1x Account Executive, Mid-Market
- 1x Chief of Staff to the Managing Director Germany (x/f/m)
- 1x Engineering Manager - Observability & Reliability Engineering Obsession (x/f/m)
- 1x Medical Expert (x/f/m)
- 1x Patient Growth Marketing Manager (x/f/m)
- 1x Senior ML Ops Engineer (x/f/m)
- 1x Workplace Experience Lead (x/f/m)
- 1x Brand Ambassador NL (Telefonisch)
- 1x Sales Representative
- 1x Telesales agent
- 1x Verkoper (Vlaanderen)
- 1x Operations Associate (20/25 Hours) - Via Del Babuino, Rome
- 1x Sales Associate - Via Del Babuino, Rome
- 1x Chef de produit senior
- 1x Chef.fe de produit senior
- 1x Développeur/développeuse de logiciel principal(e)
- 1x Développeur/développeuse de logiciels principal(e)
- 1x Développeur/Développeuse de logiciels senior
- 1x Développeur/développeuse logiciel
- 1x Développeur/développeuse logiciel senior
- 1x Développeur/développeuse senior, plateforme
- 1x Gestionnaire, développement logiciel (GO)
- 1x Gestionnaire en comptabilité
- 1x Responsable des comptes partenaires
- 1x Responsable du développement logiciel - Facturation
- 1x Responsables des comptes fournisseurs
- 1x Spécialiste de la mise en œuvre du programme Microsoft
- 1x Data Analyst - Casablanca
- 1x Customer Success Champion - on site
- 1x Senior Machine Learning Engineer
- 1x Business Development Representative
- 1x Growth Manager
- 1x Software Engineer I -  Development Program 2026
- 1x (Associate) Consultant (m/w/d) CRM & Service Transformation
- 1x (Associate) Consultant (m/w/d) Customer Experience Strategy
- 1x (Associate) Consultant (m/w/d) Public Sector – Digitale Transformation mit SAP
- 1x Senior Consultant / Manager (m/w/d) Customer Experience Strategy
- 1x Senior Consultant/Manager (m/w/d) Service Transformation

## Top 50 unknown
- 2x Manager, Account Management SMB
- 1x Lead Project Manager
- 1x Fleet Specialist
- 1x Sales Associate_도산 플래그십
- 1x Sales Associate_한남점(FT/PT30)
- 1x Store Manager (Future Talent)
- 1x Frontend Engineer
- 1x CXオペレーションサポート
- 1x Director Tax
- 1x Principal I, Program Management - Retail Program
- 1x Principal Product Manager
- 1x Product Manager II (Advertiser Acquisition Product)
- 1x Senior Data Analyst (Coupang Eats)
- 1x Senior Incident Specialist
- 1x Senior Principal, Field Sales
- 1x WFM Analyst
- 1x プロデューサー、アニメコープロダクション
- 1x シニア・プロデューサー、アニメコープロダクション
- 1x アソシエイト・プロデューサー、アニメコープロダクション
- 1x Partner Solutions Architect
- 1x SAP FI Developer
- 1x SAP MM Consultant
- 1x Senior PP Consultant
- 1x クライアントオンボーディング・アソシエイト
- 1x 口座開設手続きサポート
- 1x クライアントサービス担当者
- 1x Sales Manager, Tokyo - Japan
- 1x [Finance Div.] 연결회계팀원 (3~8년 / 계약직)
- 1x [HR Div.] 자회사 HR Specialist (8년 이상)
- 1x [Infra Div.] IT 구매 및 경영 지원 담당자 (2년 이상 / 계약직)
- 1x [Space & Property Center] 용인 정글캠퍼스 편의시설 및 운영지원 담당자 (2년 이상 / 계약직)
- 1x Lead Store Advisor, Tokyo Ginza
- 1x Store Advisor, Hannam Store
- 1x Store Advisor, The Hyundai Seoul
- 1x Store Advisor, Tokyo Ginza
- 1x Product PMO
- 1x [PUBG STUDIOS] Animator - PUBG: BLINDSPOT (5년 이상)
- 1x [PUBG STUDIOS] Client Programmer (Game Content) - Project Uropa (2년 이상)
- 1x [PUBG STUDIOS] Client Programmer (Gameplay) - Project Uropa (3년 이상)
- 1x [PUBG STUDIOS] Client Programmer (Mobile Platform & Outgame System) - Project Uropa (3년 이상)
- 1x [PUBG STUDIOS] Game Programmer - PUBG: BLINDSPOT (3년 이상)
- 1x [PUBG STUDIOS] Level Designer - PUBG: BLINDSPOT (3년 이상)
- 1x [PUBG STUDIOS] TA - Project Uropa (5년 이상)
- 1x Medical Assistant / 医疗助理
- 1x プラットフォームサポートエンジニア
- 1x Editorial Manager - PlayStation Store
- 1x ゲームプレイプログラマー・Gameplay Programmer/Team ASOBI
- 1x 【ITで支えるPlayStationの未来】業務システムアナリスト/アーキテクト（コーポレート領域)
- 1x ITサポート チームリード (グローバル連携の推進)
- 1x ITサポート マネージャー (グローバル連携の推進)
