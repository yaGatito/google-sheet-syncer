IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'products')
BEGIN
    CREATE DATABASE products;
END;
GO

USE products;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Products')
BEGIN
    CREATE TABLE Products (
        id VARCHAR(50) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        [desc] NVARCHAR(MAX) NOT NULL,
        [type] VARCHAR(100) NOT NULL,
        amount INT NOT NULL
    );
END;
GO
