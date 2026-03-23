CREATE TABLE veiculo (
    veiculo_id SERIAL PRIMARY KEY,
    modelo_caminhao VARCHAR(60),
    placa VARCHAR(30),
    capacidade_maxima FLOAT,
    capacidade_disponivel FLOAT,
    autonomia_total INTEGER
);

CREATE TABLE rota (
    rota_id SERIAL PRIMARY KEY,
    rua VARCHAR(180),
    numero INTEGER,
    cidade VARCHAR(60),
    complemento VARCHAR(180),
    cep VARCHAR(11),
    veiculo_designado_rota INTEGER REFERENCES veiculo(veiculo_id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

CREATE TABLE produto (
    produto_id SERIAL PRIMARY KEY,
    nome VARCHAR(30),
    quantidade INTEGER,
    peso FLOAT,
    nivel_criticidade INTEGER,
    janela_entrega VARCHAR(30),
    rota_designada_produto INTEGER REFERENCES rota(rota_id),
    veiculo_designado_produto INTEGER REFERENCES veiculo(veiculo_id)
);

CREATE TABLE ponto_base (
    ponto_base_id SERIAL PRIMARY KEY,
    rua VARCHAR(180),
    numero INTEGER,
    cidade VARCHAR(100),
    cep VARCHAR(11),
    veiculo_id INTEGER REFERENCES veiculo(veiculo_id),
    nome_da_base VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- 1) Veículos
INSERT INTO veiculo (veiculo_id, modelo_caminhao, placa, capacidade_maxima, capacidade_disponivel, autonomia_total) VALUES
(1, 'Mercedes Accelo 1016', 'QRT-4821', 1200.0, 1200.0, 400),
(2, 'Ford Cargo 1317', 'HNZ-7053', 800.0, 800.0, 300),
(3, 'VW Delivery 8-160', 'MWJ-2396', 1500.0, 1500.0, 500);

-- 2) Ponto base (um por veículo)
INSERT INTO ponto_base (ponto_base_id, rua, numero, cidade, cep, veiculo_id, nome_da_base, latitude, longitude) VALUES
(1, 'Av. Goiás', 1000, 'Goiânia', '74010010', 1, 'Base Central Goiânia', -16.680000, -49.256000),
(2, 'Quadra 104 Norte', 100, 'Palmas', '77006010', 2, 'Base Central Palmas', -10.172000, -48.340000),
(3, 'Avenida Afonso Pena', 1500, 'Belo Horizonte', '30130004', 3, 'Base Central BH', -19.924000, -43.938000);

-- Veículo 1 (Goiás)
INSERT INTO rota (rota_id, rua, numero, cidade, complemento, cep, veiculo_designado_rota, latitude, longitude) VALUES
(1, 'Rua 7', 230, 'Goiânia', 'Próx. Hospital A', '74020020', 1, -16.669000, -49.254000),
(2, 'Avenida Goiás', 1500, 'Goiânia', 'Centro', '74013010', 1, -16.675000, -49.260000),
(3, 'Rua 3', 400, 'Goiânia', 'Setor Central', '74020020', 1, -16.671000, -49.252000),
(4, 'Avenida Anhanguera', 800, 'Goiânia', 'Setor Universitário', '74610010', 1, -16.678000, -49.258000),
(5, 'Rua 57', 120, 'Goiânia', 'Setor Marista', '74160020', 1, -16.693000, -49.260000),
(6, 'Avenida 44', 560, 'Goiânia', 'Setor Bueno', '74215010', 1, -16.700000, -49.269000),
(19, 'Rua T-37', 900, 'Goiânia', 'Setor Bueno', '74215060', 1, -16.704000, -49.272000),
(20, 'Avenida T-9', 1200, 'Goiânia', 'Jardim América', '74255020', 1, -16.712000, -49.273000),
(21, 'Rua 85', 350, 'Goiânia', 'Setor Sul', '74085020', 1, -16.716000, -49.263000),
(22, 'Avenida Perimetral Norte', 1800, 'Goiânia', 'Jardim Nova Esperança', '74465020', 1, -16.642000, -49.298000),
(23, 'Rua C-149', 670, 'Goiânia', 'Jardim América', '74255050', 1, -16.720000, -49.277000),
(24, 'Avenida Independência', 500, 'Aparecida de Goiânia', 'Centro', '74905010', 1, -16.828000, -49.248000),
(25, 'Rua Bela Vista', 320, 'Aparecida de Goiânia', 'Bela Vista', '74906020', 1, -16.818000, -49.254000),
(26, 'Avenida Dom Emanuel', 750, 'Aparecida de Goiânia', 'Cidade Livre', '74907030', 1, -16.835000, -49.262000),
(27, 'Rua Jataí', 280, 'Anápolis', 'Centro', '75020010', 1, -16.329000, -48.953000),
(28, 'Avenida Brasil Norte', 1100, 'Anápolis', 'Centro', '75025010', 1, -16.332000, -48.948000),
(29, 'Rua Engenheiro Portela', 450, 'Anápolis', 'Centro', '75023020', 1, -16.325000, -48.956000),
(30, 'Rua General Clark', 780, 'Goiânia', 'Setor Aeroporto', '74070040', 1, -16.682000, -49.219000),
(31, 'Avenida Mutirão', 1600, 'Goiânia', 'Setor Novo Horizonte', '74365020', 1, -16.660000, -49.291000),
(32, 'Rua 9 de Julho', 980, 'Goiânia', 'Setor Oeste', '74110050', 1, -16.691000, -49.278000);

-- Veículo 2 (Tocantins)
INSERT INTO rota (rota_id, rua, numero, cidade, complemento, cep, veiculo_designado_rota, latitude, longitude) VALUES
(7, 'Quadra 208 Sul', 12, 'Palmas', 'Próx. Hospital Regional', '77021010', 2, -10.183000, -48.332000),
(8, 'Quadra 404 Norte', 56, 'Palmas', 'Próx. Clínica', '77006050', 2, -10.176000, -48.328000),
(9, 'Avenida Teotônio Segurado', 1200, 'Palmas', 'Centro', '77064050', 2, -10.189000, -48.335000),
(10, 'Quadra 104 Norte', 80, 'Palmas', 'Apto 5', '77006010', 2, -10.172000, -48.340000),
(11, 'Rua NS-01', 500, 'Palmas', 'Plano Diretor Norte', '77006070', 2, -10.165000, -48.344000),
(12, 'Avenida LO-02', 750, 'Palmas', 'Centro', '77021060', 2, -10.192000, -48.320000),
(33, 'Quadra 506 Norte', 234, 'Palmas', 'Centro Norte', '77006090', 2, -10.158000, -48.347000),
(34, 'Avenida Juscelino Kubitschek', 2100, 'Palmas', 'Centro', '77064070', 2, -10.196000, -48.342000),
(35, 'Quadra 604 Sul', 88, 'Palmas', 'Plano Diretor Sul', '77023090', 2, -10.207000, -48.335000),
(36, 'Rua dos Girassóis', 100, 'Palmas', 'Centro Cívico', '77001054', 2, -10.185000, -48.334000),
(37, 'Rua Leste 1', 450, 'Araguaína', 'Centro', '77804010', 2, -7.191000, -48.206000),
(38, 'Avenida Couto Magalhães', 800, 'Araguaína', 'Centro', '77804020', 2, -7.196000, -48.210000),
(39, 'Rua Deputado Darcy Barreto', 350, 'Araguaína', 'Setor Industrial', '77803010', 2, -7.182000, -48.198000),
(40, 'Rua Couto Magalhães', 600, 'Gurupi', 'Centro', '77405010', 2, -11.727000, -49.068000),
(41, 'Avenida Pará', 1500, 'Gurupi', 'Setor Central', '77405020', 2, -11.732000, -49.072000),
(42, 'Rua 14', 280, 'Gurupi', 'Setor Central', '77406010', 2, -11.726000, -49.063000),
(43, 'Rua 03', 730, 'Palmas', 'Plano Diretor Norte', '77006030', 2, -10.160000, -48.350000);

-- Veículo 3 (Minas Gerais)
INSERT INTO rota (rota_id, rua, numero, cidade, complemento, cep, veiculo_designado_rota, latitude, longitude) VALUES
(13, 'Avenida Afonso Pena', 800, 'Belo Horizonte', 'Centro', '30130001', 3, -19.924000, -43.938000),
(14, 'Rua da Bahia', 1200, 'Belo Horizonte', 'Próx. Laboratório', '30160011', 3, -19.921000, -43.940000),
(15, 'Avenida Brasil', 500, 'Belo Horizonte', 'Apto 3', '30140001', 3, -19.927000, -43.935000),
(16, 'Rua Espírito Santo', 1800, 'Belo Horizonte', 'Próx. Hospital das Clínicas', '30160030', 3, -19.920000, -43.945000),
(17, 'Avenida do Contorno', 4200, 'Belo Horizonte', 'Clínica Z', '30110080', 3, -19.932000, -43.948000),
(18, 'Rua Carijós', 700, 'Belo Horizonte', 'Farmácia', '30120060', 3, -19.916000, -43.934000),
(44, 'Avenida Getúlio Vargas', 1500, 'Belo Horizonte', 'Savassi', '30112020', 3, -19.938000, -43.938000),
(45, 'Rua Sergipe', 900, 'Belo Horizonte', 'Funcionários', '30130170', 3, -19.929000, -43.932000),
(46, 'Avenida Raja Gabaglia', 1800, 'Belo Horizonte', 'Luxemburgo', '30350540', 3, -19.952000, -43.956000),
(47, 'Rua Grão Pará', 440, 'Belo Horizonte', 'Santa Efigênia', '30150340', 3, -19.918000, -43.919000),
(48, 'Avenida Antônio Carlos', 6627, 'Belo Horizonte', 'Pampulha', '31270901', 3, -19.871000, -43.967000),
(49, 'Rua dos Inconfidentes', 1500, 'Uberlândia', 'Centro', '38400128', 3, -18.918000, -48.275000);

INSERT INTO produto (produto_id, nome, quantidade, peso, nivel_criticidade, janela_entrega, rota_designada_produto, veiculo_designado_produto) VALUES
(1,  'Soro 500ml - Caixa', 10, 6.0, 3, '08:00 - 12:00', 1, 1),
(2,  'Máscara N95 - Pct 20', 1, 1.0, 3, '08:00 - 10:00', 1, 1),
(3,  'Insulina - Caixa', 5, 2.5, 3, '09:00 - 11:00', 2, 1),
(4,  'Curativo Esteril - Pct', 3, 0.9, 2, '08:00 - 18:00', 2, 1),
(5,  'Oxímetro - Unidade', 2, 0.6, 3, '10:00 - 14:00', 3, 1),
(6,  'Kit Cirúrgico - Caixa', 1, 12.0, 3, '08:00 - 10:00', 3, 1),
(7,  'Caixa Equipamentos (médio)', 1, 35.0, 3, '09:00 - 16:00', 4, 1),
(8,  'Vacina Frio - Caixa', 8, 4.0, 3, '08:00 - 12:00', 4, 1),
(9,  'Luvas Estéril - Pct 100', 1, 2.0, 2, '08:00 - 18:00', 5, 1),
(10, 'Soro 1000ml - Caixa', 4, 5.0, 3, '12:00 - 16:00', 5, 1),
(11, 'Gaze - Pct', 10, 1.0, 1, '08:00 - 18:00', 6, 1),
(12, 'Analgésico - Caixa', 6, 2.4, 2, '08:00 - 18:00', 6, 1),
(13, 'Soro 500ml - Caixa', 8, 4.8, 3, '08:00 - 11:00', 7, 2),
(14, 'Máscara Cirúrgica - Pct 50', 1, 1.2, 2, '09:00 - 12:00', 7, 2),
(15, 'Insulina - Caixa', 3, 1.5, 3, '10:00 - 12:00', 8, 2),
(16, 'Oxímetro - Unidade', 1, 0.3, 3, '08:00 - 10:00', 8, 2),
(17, 'Tubos Coleta - Caixa', 5, 2.0, 2, '11:00 - 15:00', 9, 2),
(18, 'Caixa Equipamentos (grande)', 1, 45.0, 3, '08:00 - 12:00', 9, 2),
(19, 'Vacina Frio - Caixa', 6, 3.0, 3, '08:00 - 10:00', 10, 2),
(20, 'Bomba Infusão - Unidade', 1, 18.0, 3, '09:00 - 11:00', 10, 2),
(21, 'Luvas - Pct 200', 2, 4.0, 1, '08:00 - 18:00', 11, 2),
(22, 'Sonda NE - Pct', 3, 1.2, 2, '13:00 - 17:00', 11, 2),
(23, 'Gaze - Pct', 8, 0.8, 1, '08:00 - 18:00', 12, 2),
(24, 'Analgésico - Caixa', 4, 1.6, 2, '11:00 - 16:00', 12, 2),
(25, 'Soro 500ml - Caixa', 6, 3.6, 3, '08:00 - 12:00', 13, 3),
(26, 'Máscara N95 - Pct 10', 1, 0.5, 3, '09:00 - 11:00', 13, 3),
(27, 'Insulina - Caixa', 4, 2.0, 3, '08:00 - 10:00', 14, 3),
(28, 'Oxímetro - Unidade', 1, 0.3, 3, '10:00 - 14:00', 14, 3),
(29, 'Caixa Equipamentos (médio)', 1, 30.0, 3, '08:00 - 12:00', 15, 3),
(30, 'Vacina Frio - Caixa', 5, 2.5, 3, '08:00 - 09:30', 15, 3),
(31, 'Luvas - Pct 100', 2, 2.0, 1, '08:00 - 18:00', 16, 3),
(32, 'Bomba Infusão - Unidade', 1, 18.0, 3, '09:00 - 12:00', 16, 3),
(33, 'Gaze - Pct', 6, 0.6, 1, '08:00 - 18:00', 17, 3),
(34, 'Analgésico - Caixa', 3, 1.2, 2, '11:00 - 15:00', 17, 3),
(35, 'Sonda NE - Pct', 2, 0.8, 2, '08:00 - 13:00', 18, 3),
(36, 'Oxímetro - Reserva', 1, 0.4, 3, '13:00 - 17:00', 18, 3),
(37, 'Soro Fisiológico 500ml', 6, 3.6, 3, '08:00 - 11:00', 19, 1),
(38, 'Luvas Nitrílicas - Pct 100', 2, 2.0, 2, '08:00 - 18:00', 19, 1),
(39, 'Vacina Termolábil - Caixa', 4, 2.0, 3, '08:00 - 10:00', 20, 1),
(40, 'Gaze Estéril - Pct', 5, 0.5, 1, '08:00 - 18:00', 20, 1),
(41, 'Insulina Refrigerada', 3, 1.5, 3, '09:00 - 11:00', 21, 1),
(42, 'Seringa Descartável - Pct', 2, 0.8, 2, '08:00 - 18:00', 21, 1),
(43, 'Oxímetro Portátil', 1, 0.4, 3, '10:00 - 14:00', 22, 1),
(44, 'Kit Curativo Avançado', 1, 1.2, 2, '08:00 - 16:00', 22, 1),
(45, 'Caixa Equipamentos Leves', 1, 20.0, 3, '09:00 - 15:00', 23, 1),
(46, 'Termômetro Digital', 3, 0.9, 1, '08:00 - 18:00', 23, 1),
(47, 'Medicamentos Controlados', 2, 1.6, 3, '08:00 - 12:00', 24, 1),
(48, 'Máscara Cirúrgica - Pct 50', 1, 1.2, 1, '08:00 - 18:00', 24, 1),
(49, 'Sonda Vesical - Pct', 2, 1.0, 2, '09:00 - 13:00', 25, 1),
(50, 'Luvas Estéreis - Pct 50', 1, 1.0, 1, '08:00 - 18:00', 25, 1),
(51, 'Vacina Frio - Caixa', 5, 2.5, 3, '08:00 - 10:00', 33, 2),
(52, 'Caixa Isotérmica', 1, 6.0, 2, '08:00 - 12:00', 33, 2),
(53, 'Bomba de Infusão', 1, 18.0, 3, '09:00 - 11:00', 34, 2),
(54, 'Equipo Macrogotas', 4, 1.2, 2, '08:00 - 18:00', 34, 2),
(55, 'Soro Glicosado', 6, 4.2, 3, '10:00 - 13:00', 35, 2),
(56, 'Luvas Latex - Pct 100', 2, 2.0, 1, '08:00 - 18:00', 35, 2),
(57, 'Kit Emergência Médica', 1, 22.0, 3, '08:00 - 12:00', 36, 2),
(58, 'Oxímetro Reserva', 1, 0.4, 2, '13:00 - 17:00', 36, 2),
(59, 'Medicamentos Refrigerados', 3, 1.8, 3, '08:00 - 10:00', 37, 2),
(60, 'Termômetro Clínico', 2, 0.6, 1, '08:00 - 18:00', 37, 2),
(61, 'Caixa Equipamentos Pesados', 1, 48.0, 3, '09:00 - 15:00', 38, 2),
(62, 'Avental Cirúrgico', 3, 1.5, 2, '08:00 - 18:00', 38, 2),
(63, 'Soro Fisiológico 1L', 4, 5.0, 3, '08:00 - 11:00', 44, 3),
(64, 'Luvas Nitrílicas - Pct 100', 1, 1.0, 1, '08:00 - 18:00', 44, 3),
(65, 'Vacina Termossensível', 3, 1.5, 3, '08:00 - 09:30', 45, 3),
(66, 'Caixa Térmica Pequena', 1, 4.0, 2, '08:00 - 12:00', 45, 3),
(67, 'Equipamento Monitor Cardíaco', 1, 28.0, 3, '09:00 - 14:00', 46, 3),
(68, 'Sensor Cardíaco', 2, 1.0, 2, '08:00 - 18:00', 46, 3),
(69, 'Medicamentos Injetáveis', 4, 2.0, 3, '10:00 - 13:00', 47, 3),
(70, 'Seringas Descartáveis', 3, 1.2, 1, '08:00 - 18:00', 47, 3),
(71, 'Kit Atendimento Domiciliar', 1, 15.0, 2, '09:00 - 16:00', 48, 3),
(72, 'Oxímetro Portátil', 1, 0.4, 2, '13:00 - 17:00', 48, 3),
(73, 'Gaze Estéril - Pct', 6, 0.6, 1, '08:00 - 18:00', 49, 3),
(74, 'Analgésico Injetável', 2, 0.8, 2, '11:00 - 15:00', 49, 3);

-- Atualiza as sequences após inserts com IDs explícitos
SELECT setval('veiculo_veiculo_id_seq', (SELECT MAX(veiculo_id) FROM veiculo));
SELECT setval('rota_rota_id_seq', (SELECT MAX(rota_id) FROM rota));
SELECT setval('produto_produto_id_seq', (SELECT MAX(produto_id) FROM produto));
SELECT setval('ponto_base_ponto_base_id_seq', (SELECT MAX(ponto_base_id) FROM ponto_base));
