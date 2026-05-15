-- Generated SQL INSERT statements for invoices
-- Generated at: 2026-05-15 11:19:40
-- Total records: 9

CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(100),
    invoice_date VARCHAR(50),
    tracking_number VARCHAR(100),
    company_name VARCHAR(255),
    total_amount DECIMAL(15,2),
    currency VARCHAR(10),
    phone VARCHAR(50),
    fax VARCHAR(50),
    item_count INT,
    source_file VARCHAR(255),
    source_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO invoices (invoice_number, tracking_number, company_name, total_amount, currency, phone, fax, item_count, source_file, source_path)
VALUES ('KTB0911-X52-S01-24538', 'LDX:506538778406', 'Importer SANEI SANSYOU CORPORATION', 913.0, 'JPY', '', '', 55, 'インボイス見本_all_pages.txt', 'results\20260515_111347\インボイス見本_all_pages.txt');

INSERT INTO invoices (currency, item_count, source_file, source_path)
VALUES ('USD', 4, 'インボイス見本_page_0001.txt', 'results\20260515_111347\インボイス見本_page_0001.txt');

INSERT INTO invoices (invoice_number, company_name, currency, phone, fax, item_count, source_file, source_path)
VALUES ('KTB0911-X52-S01-24538', 'Importer SANEI SANSYOU CORPORATION', 'JPY', '', '', 3, 'インボイス見本_page_0002.txt', 'results\20260515_111347\インボイス見本_page_0002.txt');

INSERT INTO invoices (tracking_number, company_name, currency, phone, fax, item_count, source_file, source_path)
VALUES ('LDX:506538778406', 'UK LIANTAI COLTD', 'JPY', '00442084323088', '00442084323088', 18, 'インボイス見本_page_0003.txt', 'results\20260515_111347\インボイス見本_page_0003.txt');

INSERT INTO invoices (currency, item_count, source_file, source_path)
VALUES ('USD', 21, 'インボイス見本_page_0004.txt', 'results\20260515_111347\インボイス見本_page_0004.txt');

INSERT INTO invoices (currency, phone, fax, item_count, source_file, source_path)
VALUES ('USD', '', '', 0, 'インボイス見本_page_0005.txt', 'results\20260515_111347\インボイス見本_page_0005.txt');

INSERT INTO invoices (currency, item_count, source_file, source_path)
VALUES ('USD', 2, 'インボイス見本_page_0006.txt', 'results\20260515_111347\インボイス見本_page_0006.txt');

INSERT INTO invoices (total_amount, currency, phone, fax, item_count, source_file, source_path)
VALUES (913.0, 'JPY', '86', '86', 0, 'インボイス見本_page_0007.txt', 'results\20260515_111347\インボイス見本_page_0007.txt');

INSERT INTO invoices (currency, phone, item_count, source_file, source_path)
VALUES ('USD', '83150820', 7, 'インボイス見本_page_0008.txt', 'results\20260515_111347\インボイス見本_page_0008.txt');

