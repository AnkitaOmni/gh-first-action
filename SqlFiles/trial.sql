SELECT
    RetId,
    Ruth,
    SUM(FinalAmt) AS TotalFinalAmt,
    SUBSTRING_INDEX(GROUP_CONCAT(SUBSTRING_INDEX(DocNum, "NAN", 1) ORDER BY DocNum DESC), ",", 1) AS LatestIDP

FROM chile_report

WHERE
    Ruth IN (
        SELECT Ruth
        FROM chile_report
        GROUP BY Ruth
        HAVING count(Ruth) > 1
    )
GROUP BY Ruth;


SELECT
    SUBSTRING_INDEX(GROUP_CONCAT(SUBSTRING_INDEX(DocNum, "NAN", 1) ORDER BY DocNum DESC) ",", 1) AS LatestIDP
FROM chile_report
