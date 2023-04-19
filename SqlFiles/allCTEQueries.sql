-- ################################################################################################### 
-- * ################################## CCX24 Update Retailer Data  ################################## 
-- ################################################################################################### 


WITH cte_two AS (
    WITH cte_one AS (
        SELECT DISTINCT CONCAT(RetId,"#^#",InsId) AS RetId_InsId, IDP
        FROM fulldaytransactionretailerhistory
        WHERE IDP IN (SELECT DISTINCT DocNum FROM chileidpupdate)
    UNION
        SELECT DISTINCT CONCAT(RetId,"#^#",InsId) AS RetId_InsId, IDP
        FROM fulldaytransactionretailerhistory
        WHERE IDP IN (SELECT DISTINCT IDP FROM estadoidpupdate)
    )
    SELECT
        IDP, RetailerId AS RetId, EntityId AS InsId, IdentificationNumber AS Ruth, 
        SUBSTRING_INDEX (IdentificationNumber, '-', -1) AS Dv, Name, AccountNumber AS AcNum, 
        CASE WHEN BankCode = "012" THEN "Estado" ELSE "991" END AS DocType, 
        ChileEstadoAccountType(BankCode, MovmentType) AS AcType,
        BankCode AS BankCode
    FROM
    (
        SELECT * FROM cte_one cto 
        INNER JOIN retailerid rid 
        ON CONCAT(rid.RetailerId, "#^#", rid.EntityId) = cto.RetId_InsId
    )
    AS LatestData
)
UPDATE fulldaytransactionretailerhistory AS fthr, cte_two AS ct2
SET
    fthr.Ruth = ct2.Ruth,
    fthr.Dv = ct2.Dv,
    fthr.RetName = ct2.Name,
    fthr.AcNum = ct2.AcNum,
    fthr.DocType = ct2.DocType,
    fthr.AcType = ct2.AcType,
    fthr.BankCode = ct2.BankCode
WHERE
fthr.IDP = ct2.IDP;