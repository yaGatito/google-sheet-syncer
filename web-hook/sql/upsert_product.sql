MERGE Products AS target
USING (
    SELECT
        %s AS id,
        %s AS name,
        %s AS [desc],
        %s AS [type],
        %s AS amount,
        %s AS extra
) AS source
ON target.id = source.id

WHEN MATCHED THEN
    UPDATE SET
        target.name = source.name,
        target.[desc] = source.[desc],
        target.[type] = source.[type],
        target.amount = source.amount,
        target.extra = source.extra

WHEN NOT MATCHED THEN
    INSERT (id, name, [desc], [type], amount, extra)
    VALUES (
        source.id,
        source.name,
        source.[desc],
        source.[type],
        source.amount,
        source.extra
    );
