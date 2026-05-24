/*
Contrato esperado pela UI VPS (ordem + tipo_bloco):
colunas obrigatorias:
  [order]       int
  [block_id]    varchar
  [title]       varchar (opcional se existir no template_catalog)
  [tipo_bloco]  varchar (opcional se existir no template_catalog)
  [template]    varchar (opcional se existir no template_catalog)
  [source_ref]  varchar
  [data]        nvarchar(max) JSON

Exemplo para SQL Server:
*/

SELECT
  CAST([ordem] AS int)                                   AS [order],
  CAST([codigo_bloco] AS varchar(80))                    AS [block_id],
  CAST([titulo_bloco] AS varchar(255))                   AS [title],
  CAST([tipo_bloco] AS varchar(80))                      AS [tipo_bloco],
  CAST([template] AS varchar(120))                       AS [template],
  CAST('vw_vps_payload_oficial' AS varchar(120))         AS [source_ref],
  CAST([data_json] AS nvarchar(max))                     AS [data]
FROM [dbo].[vw_vps_payload_oficial]
WHERE [ativo] = 1
ORDER BY [ordem] ASC;
