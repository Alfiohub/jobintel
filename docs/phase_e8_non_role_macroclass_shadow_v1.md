# Phase E.8.1 — Shadow Non-Role Macro-Class Draft

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows total: `81011`
- other before: `35952`

## Shadow Result
- non-role candidates total: `563`
- from other: `459`
- from matched: `104`
- occupational other after shadow: `35493`
- delta occupational other: `-459`

## Top Pattern Hits
- `description:keep your information on file`: `118`
- `title:talent community`: `95`
- `description:join our talent community`: `70`
- `description:send us your resume`: `67`
- `title:future opportunities`: `64`
- `description:future openings`: `61`
- `title:general application`: `60`
- `title:talent pool`: `43`
- `description:don't see an opportunity`: `32`
- `title:future opportunity`: `31`
- `title:general interest`: `29`
- `title:expression of interest`: `22`
- `title:open application`: `20`
- `title:don't see what you're looking for`: `18`
- `description:drop your resume`: `14`

## Sample Other -> Non-Role
- `Interested in joining our team?` | company `gomotive` | hits `description:send us your resume, description:keep your information on file, description:don't see an opportunity`
- `Interested in joining our team?` | company `gomotive` | hits `description:send us your resume, description:keep your information on file, description:don't see an opportunity`
- `Lead Instructor: Cybersecurity (General Interest)` | company `correlationone` | hits `title:general interest`
- `Lead Instructor: Data Analytics (General Interest)` | company `correlationone` | hits `title:general interest`
- `Expression of Interest: Senior Growth Manager (Ad Sales)` | company `moloco` | hits `title:expression of interest`
- `General Interest - Future Consideration` | company `xapo61` | hits `title:general interest, title:future consideration`
- `Associate, Axios Live - Talent Pool` | company `axios` | hits `title:talent pool`
- `Associate, Business Development - Talent Pool` | company `axios` | hits `title:talent pool, description:future openings`
- `AI Mentor Talent Pool - Contractor Roles` | company `udacity` | hits `title:talent pool`
- `Apply for future opportunities` | company `flywheeldigital` | hits `title:future opportunities, description:keep your information on file`
- `AI Talent Pool` | company `doctolib` | hits `title:talent pool`
- `Don't see the right job listed? Submit your application here to join our general talent pool.` | company `pomelocare` | hits `title:talent pool`

## Sample Matched -> Non-Role
- `Future Sales Openings: Account Executive, US - Remote` | current `account_executive/sales` | rule `sales_account_exec` | hits `description:keep your information on file`
- `Expression of Interest: Machine Learning Engineer` | current `ml_engineer/machine_learning` | rule `eng_ml` | hits `title:expression of interest`
- `Account Executive - DACH (Future Talent Opportunity)` | current `account_executive/sales` | rule `sales_account_exec` | hits `description:keep your information on file`
- `Account Executive - DACH (Future Talent Opportunity)` | current `account_executive/sales` | rule `sales_account_exec` | hits `description:keep your information on file`
- `Account Executive - DACH (Future Talent Opportunity)` | current `account_executive/sales` | rule `sales_account_exec` | hits `description:keep your information on file`
- `Account Executive - DACH (Future Talent Opportunity)` | current `account_executive/sales` | rule `sales_account_exec` | hits `description:keep your information on file`
- `ISP - OSP Task Order Project Manager (Future Opportunity)` | current `project_manager/program_management` | rule `program_project_manager` | hits `title:future opportunity`
- `Program Manager (Future Opportunity)` | current `project_manager/program_management` | rule `program_project_manager` | hits `title:future opportunity`
- `Talent Pool Account Executive - Italian Market` | current `account_executive/sales` | rule `sales_account_exec` | hits `title:talent pool`
- `Talent Pool Account Executive - Portuguese Market` | current `account_executive/sales` | rule `sales_account_exec` | hits `title:talent pool`
- `Talent Pool Account Executive - Spanish Market` | current `account_executive/sales` | rule `sales_account_exec` | hits `title:talent pool, description:keep your information on file`
- `Account Director, Campaigns` | current `account_manager/sales` | rule `sales_account_director` | hits `description:keep your information on file`

## Recommendation
- `shadow_non_role_macroclass_viable`
- reason: The dataset contains a measurable recruiting-placeholder slice that should be separated from occupational coding before future residual analysis.
