import asyncio
import logging
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.product import Product
from app.services.typesense_service import (
    upsert_product_document,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(str(settings.DATABASE_URL))
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# --- Catálogo estático de ejemplos ---
CATALOG_SEED = {
    "tecnologia": [
        (
            "Audífonos Bluetooth In-Ear XYZ",
            "Perfectos para estudiar en el campus, cancelación de ruido activa y 24 horas de batería. Subcategoría: Audio.",
            150000,
            "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?q=80&w=600",
        ),
        (
            "Mouse Inalámbrico Ergonómico",
            "Evita el túnel carpiano. Ideal para largas jornadas de código. DPI ajustable. Subcategoría: Accesorios.",
            45000,
            "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?q=80&w=600",
        ),
        (
            "Teclado Mecánico RGB",
            "Switches red para no hacer ruido en clase. Formato 60%. Subcategoría: Periféricos.",
            120000,
            "https://images.unsplash.com/photo-1595225476474-87563907a212?q=80&w=600",
        ),
        (
            "Cargador de carga rápida 65W",
            "Permite cargar tanto el celular como el portátil por Type-C. Subcategoría: Accesorios.",
            65000,
            "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?q=80&w=600",
        ),
        (
            "Laptop Gamer de Segunda",
            "RTX 3060, 16GB RAM, la vendo porque necesito plata para semestre final. Subcategoría: Computación.",
            2500000,
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=600",
        ),
        (
            "Monitor IPS 24 Pulgadas",
            "Sin marcos, 75hz. Incluye cable HDMI. Subcategoría: Monitores.",
            350000,
            "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?q=80&w=600",
        ),
        (
            "Pendrive 64GB USB 3.0",
            "Veloz y confiable, lo dejo barato. Subcategoría: Almacenamiento.",
            25000,
            "https://images.unsplash.com/photo-1601053075043-9828cc384ba2?q=80&w=600",
        ),
        (
            "PowerBank 10000mAh",
            "Nunca te quedes sin batería en el parcial. Marca reconocida. Subcategoría: Baterías.",
            38000,
            "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?q=80&w=600",
        ),
        (
            "Base refrigerante para portátil",
            "Dos ventiladores y luces azules. Subcategoría: Accesorios Laptop",
            30000,
            "https://images.unsplash.com/photo-1627918335025-055de7fb739d?q=80&w=600",
        ),
        (
            "Funda protectora para MacBook 13",
            "Color gris mate espacial. Subcategoría: Protección.",
            20000,
            "https://images.unsplash.com/photo-1611078449903-882236d39d91?q=80&w=600",
        ),
    ],
    "comida": [
        (
            "Empanada Horneada Vegana",
            "Masa de yuca con relleno de setas. Muy sana. Subcategoría: Snacks",
            3500,
            "https://images.unsplash.com/photo-1626079361665-c340a5a225ee?q=80&w=600",
        ),
        (
            "Brownie Doble Chocolate",
            "Hecho en casa, con extra nueces y cubierta crujiente. Subcategoría: Postres",
            4000,
            "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=600",
        ),
        (
            "Sándwich de Pollo Pesto",
            "Pan masa madre, pollo desmechado fresco y salsa artesanal. Subcategoría: Comida fuerte",
            8000,
            "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?q=80&w=600",
        ),
        (
            "Jugo natural Mango Biche",
            "Bien helado, te lo entrego en cafetería. Subcategoría: Bebidas",
            3000,
            "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?q=80&w=600",
        ),
        (
            "Alfajores de Maicena (Caja x6)",
            "Rellenos de mucho arequipe. Subcategoría: Postres",
            12000,
            "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?q=80&w=600",
        ),
        (
            "Ensalada César para llevar",
            "Crutones crujientes, aderezo espectacular. Subcategoría: Almuerzos",
            14000,
            "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=600",
        ),
        (
            "Galletas de Avena y Miel",
            "Tres galletones saludables para picar en clase. Subcategoría: Snacks",
            5000,
            "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?q=80&w=600",
        ),
        (
            "Croissant relleno de Nutella",
            "Recién salido del horno, súper hojaldrado. Subcategoría: Panadería",
            6500,
            "https://images.unsplash.com/photo-1558223403-d6cbf09baf2f?q=80&w=600",
        ),
        (
            "Deditos de Queso x 5",
            "Con salsa de piña casera incluida. Subcategoría: Snacks",
            7500,
            "https://images.unsplash.com/photo-1625938146369-adc8d58c0c45?q=80&w=600",
        ),
        (
            "Bowl de Frutas con Yogurt",
            "Granola, banano, fresas y yogurt natural. Subcategoría: Desayunos",
            9000,
            "https://images.unsplash.com/photo-1493770348161-369560ae357d?q=80&w=600",
        ),
    ],
    "moda": [
        (
            "Chaqueta Jean Vintage Oversize",
            "Prenda única, lavada a la piedra. Estilo streetwear. Subcategoría: Chaquetas",
            55000,
            "https://images.unsplash.com/photo-1551537482-f209bfc30f4a?q=80&w=600",
        ),
        (
            "Tenis Blancos Estilo Urbano",
            "Talla 41, los usé 2 veces. Están como nuevos. Subcategoría: Calzado",
            90000,
            "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600",
        ),
        (
            "Camiseta Básica Algodón",
            "Color negro sólido, cuello redondo. Corte clásico. Subcategoría: Camisetas",
            25000,
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=600",
        ),
        (
            "Sudadera Negra Ajustada",
            "Perfecta para ir al gimnasio de la U. Talla M. Subcategoría: Ropa deportiva",
            35000,
            "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=600",
        ),
        (
            "Gorro Beanie de Lana",
            "Tejido a mano, abriga muy bien para las mañanas. Subcategoría: Gorros",
            18000,
            "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?q=80&w=600",
        ),
        (
            "Gafas de Sol Estilo Retro",
            "Protección UV400, montura tortuga. Subcategoría: Accesorios",
            28000,
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600",
        ),
        (
            "Vestido Floral de Verano",
            "Tela fresca y ligera. Ideal para el calor de Cali. Subcategoría: Vestidos",
            45000,
            "https://images.unsplash.com/photo-1515347619362-e64e9a03975d?q=80&w=600",
        ),
        (
            "Reloj Clásico Acero Inoxidable",
            "Resistente al agua, cristal mineral. Subcategoría: Relojes",
            110000,
            "https://images.unsplash.com/photo-1524592094714-0f0654e20314?q=80&w=600",
        ),
        (
            "Morral Lona Porta PC",
            "Resistente al agua, varios compartimentos. Subcategoría: Maletas",
            65000,
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600",
        ),
        (
            "Correa Cuero Genuino",
            "Hebilla clásica, color café oscuro. Subcategoría: Accesorios",
            35000,
            "https://images.unsplash.com/photo-1624222247344-5c91ad05dff3?q=80&w=600",
        ),
    ],
    "academico": [
        (
            "Libro Cálculo de Stewart 7ma",
            "En buen estado, sin rayar. Imprescindible. Subcategoría: Libros de texto",
            80000,
            "https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=600",
        ),
        (
            "Calculadora Científica Casio",
            "Modelo Fx-991La X. Te salvará en parciales. Subcategoría: Calculadoras",
            90000,
            "https://images.unsplash.com/photo-1587145820266-a5951ee6f620?q=80&w=600",
        ),
        (
            "Set Resaltadores Pastel x6",
            "Marca Stabilo Boss, colores súper lindos. Subcategoría: Papelería",
            22000,
            "https://images.unsplash.com/photo-1522881451255-f59ad836fdfb?q=80&w=600",
        ),
        (
            "Cuaderno Inteligente Reutilizable",
            "Borras todo con calor o paño húmedo. Viene con bolígrafo. Subcategoría: Cuadernos",
            45000,
            "https://images.unsplash.com/photo-1531346878377-a541e4b0c5ce?q=80&w=600",
        ),
        (
            "Bata de Laboratorio Blanca",
            "Talla S, 100% algodón, normativa institucional. Subcategoría: Indumentaria",
            30000,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=600",
        ),
        (
            "Gafas de Seguridad Laboratorio",
            "Antiempañantes y antirrayaduras. Subcategoría: Protección",
            12000,
            "https://images.unsplash.com/photo-1582719202047-dfafbc1e3cb4?q=80&w=600",
        ),
        (
            "Libro Inteligencia Artificial Moderna",
            "El de Russell y Norvig, pasta dura en español. Subcategoría: Libros de ingeniería",
            120000,
            "https://images.unsplash.com/photo-1555661530-68c8e98db4e6?q=80&w=600",
        ),
        (
            "Estuche Lápices Lona Organizador",
            "Cabe de todo, muchísimos espacios. Subcategoría: Útiles",
            18000,
            "https://images.unsplash.com/photo-1590845947376-2638caa89309?q=80&w=600",
        ),
        (
            "Tablero Corcho Pequeño",
            "Decorativo para colgar tus notas e ideas. Subcategoría: Oficina",
            25000,
            "https://images.unsplash.com/photo-1586022838380-459275cb111a?q=80&w=600",
        ),
        (
            "Asesoría en Cálculo Diferencial",
            "Precio x Hora. Sacas 5 fijo. Subcategoría: Tutorías",
            25000,
            "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=600",
        ),
    ],
    "hogar": [
        (
            "Humidificador Ultrasónico Luz Led",
            "Para el cuarto o estudio. Usa gotas de esencia. Subcategoría: Decoración",
            48000,
            "https://images.unsplash.com/photo-1616423640778-28d1b53229bd?q=80&w=600",
        ),
        (
            "Lámpara de Escritorio Minimalista",
            "Blanca y de luz cálida regulable. Táctil. Subcategoría: Iluminación",
            38000,
            "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?q=80&w=600",
        ),
        (
            "Silla Ergonómica Mesh Oficina",
            "Dejó de chillar, levanta y tiene soporte lumbar. Subcategoría: Muebles",
            180000,
            "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?q=80&w=600",
        ),
        (
            "Tapete Shaggy Suave Gris",
            "1.50mx1.00m ideal para la sala de tu apartamento. Subcategoría: Decoración",
            65000,
            "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?q=80&w=600",
        ),
        (
            "Organizador Escritorio Madera",
            "Te mantiene los bolígrafos y cables ordenados. Subcategoría: Organización",
            22000,
            "https://images.unsplash.com/photo-1589578228447-e1a4e481c6c8?q=80&w=600",
        ),
        (
            "Licuadora Personal Portátil",
            "Vasito tipo termo para llevar batidos al gym/u. Subcategoría: Electrodomésticos",
            40000,
            "https://images.unsplash.com/photo-1584985226955-f6c770cce28d?q=80&w=600",
        ),
        (
            "Vela Aromática Sándalo",
            "Dura 40 horas, muy relajante. Subcategoría: Decoración",
            15000,
            "https://images.unsplash.com/photo-1603006905393-27632bea0c74?q=80&w=600",
        ),
        (
            "Almohada Viscoelástica Cervical",
            "Memory Foam para dormir mejor. Subcategoría: Cama",
            45000,
            "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?q=80&w=600",
        ),
        (
            "Macetita con Suculenta Real",
            "Decora tu rincón de estudio. Requiere poca agua. Subcategoría: Plantas",
            10000,
            "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?q=80&w=600",
        ),
        (
            "Portavasos de Corcho Divertidos",
            "Pack x6, proteje tus mesas. Subcategoría: Cocina",
            8000,
            "https://images.unsplash.com/photo-1616335198424-4ba2b06faada?q=80&w=600",
        ),
    ],
    "deportes": [
        (
            "Tapete de Yoga Antideslizante",
            "Grosor 6mm, incluye correa de transporte. Subcategoría: Yoga",
            30000,
            "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?q=80&w=600",
        ),
        (
            "Proteína Whey Vainilla (Sellada)",
            "Tarro de 2 Lbs marca nacional certificada. Subcategoría: Suplementos",
            85000,
            "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?q=80&w=600",
        ),
        (
            "Mancuernas Neopreno 5kg x2",
            "Set para entrenar brazos en casa. Subcategoría: Pesas",
            45000,
            "https://images.unsplash.com/photo-1586071477150-1375ba3ecee3?q=80&w=600",
        ),
        (
            "Balón de Fútbol N.5 Replica",
            "Para los partidos de viernes. Muy buen estado. Subcategoría: Deportes en equipo",
            35000,
            "https://images.unsplash.com/photo-1614632537423-1e6c2e7e0aab?q=80&w=600",
        ),
        (
            "Banda Elástica Resistencia Alta",
            "Color negra, para rutinas pesadas. Subcategoría: Equipo funcional",
            15000,
            "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=600",
        ),
        (
            "Termo Mezclador (Shaker)",
            "700ml con bola de acero para sin grumos. Subcategoría: Accesorios deportivos",
            12000,
            "https://images.unsplash.com/photo-1526505500589-9a74aa9f743c?q=80&w=600",
        ),
        (
            "Gorra Running Reflectiva",
            "Secado rápido y muy ligera. Subcategoría: Ropa deportiva",
            20000,
            "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?q=80&w=600",
        ),
        (
            "Rodillera Compresión Genérica",
            "Previene dolores al correr o hacer sentadilla. Subcategoría: Ortopedia deportiva",
            18000,
            "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600",
        ),
        (
            "Zapatillas Running Profesionales",
            "Están sucias nomás. Con buena suela, talla 40. Subcategoría: Calzado deportivo",
            130000,
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600",
        ),
        (
            "Creatina Monohidrato 300g",
            "Pura y sin saborizantes agregados. Crecimiento. Subcategoría: Suplementos",
            50000,
            "https://images.unsplash.com/photo-1579722820308-d74e5719e3df?q=80&w=600",
        ),
    ],
    "belleza": [
        (
            "Sérum Vitamina C",
            "Ilumina el rostro. Dermatológico. Subcategoría: Skincare",
            48000,
            "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?q=80&w=600",
        ),
        (
            "Protector Solar Toque Seco",
            "Para usar todos los días. 50 SPF. Nuevo. Subcategoría: Skincare",
            60000,
            "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?q=80&w=600",
        ),
        (
            "Paleta de Sombras Tonos Tierra",
            "Súper pigmentada, la vendo porque me regalaron otra igual. Subcategoría: Maquillaje",
            35000,
            "https://images.unsplash.com/photo-1512496115841-cadcfdbcb1e2?q=80&w=600",
        ),
        (
            "Labial Líquido Mate Larga Duración",
            "Color rojo rubí. Intransferible. Subcategoría: Labiales",
            15000,
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?q=80&w=600",
        ),
        (
            "Set de Brochas Sintéticas Profesionales",
            "Incluye 12 piezas en estuche. Subcategoría: Herramientas Maquillaje",
            28000,
            "https://images.unsplash.com/photo-1596704017254-9b121068fb31?q=80&w=600",
        ),
        (
            "Crema Hidratante para Manos Almendras",
            "Tubo bolsillo, huele increíble. Subcategoría: Cuidado corporal",
            12000,
            "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?q=80&w=600",
        ),
        (
            "Plancha de Cabello Cerámica",
            "Calienta al instante, alisa y evita el frizz. Subcategoría: Eléctricos belleza",
            95000,
            "https://images.unsplash.com/photo-1522337660859-02fbefca4702?q=80&w=600",
        ),
        (
            "Perfume Cítrico Fresco (Imitación fina)",
            "El aroma es 99% idéntico y dura 8h. Subcategoría: Fragancias",
            40000,
            "https://images.unsplash.com/photo-1594035910387-fea47794261f?q=80&w=600",
        ),
        (
            "Esponja Blender de Maquillaje",
            "Sin látex, muy suavecita al humedecerla. Subcategoría: Esponjas",
            8000,
            "https://images.unsplash.com/photo-1631245089332-95ce6ebfec81?q=80&w=600",
        ),
        (
            "Mascarilla Capilar de Argán",
            "Recupera tu pelo reseco en 15 minutos. Subcategoría: Cuidado capilar",
            25000,
            "https://images.unsplash.com/photo-1580870058778-958da5033878?q=80&w=600",
        ),
    ],
    "entretenimiento": [
        (
            "Juego PS4 The Last of Us",
            "CD inmaculado, caja completa. Subcategoría: Videojuegos",
            45000,
            "https://images.unsplash.com/photo-1605901309584-818e25960b8f?q=80&w=600",
        ),
        (
            "Control Inalámbrico Xbox Serie X",
            "Color blanco, casi no tiene uso. Subcategoría: Controles",
            180000,
            "https://images.unsplash.com/photo-1592840496694-26d035b52b48?q=80&w=600",
        ),
        (
            "Cartas UNO Flop Originales",
            "Vienen en estuche de metal, están enteras. Subcategoría: Juegos de mesa",
            20000,
            "https://images.unsplash.com/photo-1606167668585-6111fdbfb9c0?q=80&w=600",
        ),
        (
            "Cubo Rubik Profesional Magnético",
            "Lo mejor para hacer speedcubing suave. Subcategoría: Puzzles",
            35000,
            "https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?q=80&w=600",
        ),
        (
            "Libro Harry Potter Tapa Dura Edición Especial",
            "Con folia dorada. Hermoso para coleccionistas. Subcategoría: Libros",
            55000,
            "https://images.unsplash.com/photo-1618666012174-83b441c0bc76?q=80&w=600",
        ),
        (
            "Set Dados de Rol D&D Metálicos",
            "Muy pesados y elegantes. Incluyen cajita. Subcategoría: Rol",
            40000,
            "https://images.unsplash.com/photo-1608111283307-2daab7e1b1d7?q=80&w=600",
        ),
        (
            "Figura de Acción Spider-Man",
            "Original de Hasbro, 15cm articulada. Subcategoría: Coleccionables",
            65000,
            "https://images.unsplash.com/photo-1608226068254-080ed7b5c879?q=80&w=600",
        ),
        (
            "Rompecabezas de 1000 piezas Paisaje",
            "Las piezas están completas, garantizado. Subcategoría: Juegos de mesa",
            25000,
            "https://images.unsplash.com/photo-1600854425442-7a0e5b8d29b2?q=80&w=600",
        ),
        (
            "Set Pinceles Acuarela Profesional",
            "Para pintar o hacer rotulación (Lettering). Subcategoría: Arte",
            32000,
            "https://images.unsplash.com/photo-1582236528775-65ab9b068da6?q=80&w=600",
        ),
        (
            "Stickers Personalizados Pack x50",
            "Diseño de desarrollo web, anime y gaming. Subcategoría: Varios",
            10000,
            "https://images.unsplash.com/photo-1572372076043-44eb1a47343b?q=80&w=600",
        ),
    ],
    "servicios": [
        (
            "Diseño de Logo para Prendimientos",
            "Hago marcas bonitas y vectoriales. Subcategoría: Diseño Gráfico",
            90000,
            "https://images.unsplash.com/photo-1626785774573-4b799315345d?q=80&w=600",
        ),
        (
            "Peluquería y Barba a Domicilio Universitarios",
            "Voy a tu residencia con todas las herramientas. Subcategoría: Estética",
            25000,
            "https://images.unsplash.com/photo-1512690459411-b9245aed614b?q=80&w=600",
        ),
        (
            "Instalación de Windows y Office",
            "Formateo, Office y backup. Te queda rapidísimo. Subcategoría: Soporte Técnico",
            40000,
            "https://images.unsplash.com/photo-1588508065123-287b28e01bf3?q=80&w=600",
        ),
        (
            "Clases Particulares de Física",
            "Te explico con paciencia dinámica y cinemática. Subcategoría: Tutorías",
            30000,
            "https://images.unsplash.com/photo-1635328400030-cf227918a5f8?q=80&w=600",
        ),
        (
            "Cuidado de Mascotas Fin de Semana",
            "Paseo tu perrito si vas de viaje. Subcategoría: Mascotas",
            50000,
            "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=600",
        ),
        (
            "Traducción Ensayo Inglés a Español",
            "Nivel C1 certificado. Gramática impecable. Subcategoría: Traducción",
            20000,
            "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?q=80&w=600",
        ),
        (
            "Mantenimiento Portátiles Pasta Térmica",
            "Evita que se apague y queme la gráfica. Subcategoría: Soporte Técnico",
            55000,
            "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?q=80&w=600",
        ),
        (
            "Sesión de Fotos para Graduados",
            "Fotos profesionales cerca del lago de la universidad. Subcategoría: Fotografía",
            120000,
            "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=600",
        ),
        (
            "Elaboración de Hojas de Vida (CV)",
            "Diseño ATS-friendly y corrección redacción. Subcategoría: Asesoría",
            25000,
            "https://images.unsplash.com/photo-1586281380349-632531db7ed4?q=80&w=600",
        ),
        (
            "Limpieza de Calzado (Sneakers Care)",
            "Revivo tus tenis blancos, los dejo como nuevos. Subcategoría: Limpieza",
            18000,
            "https://images.unsplash.com/photo-1581563600649-4eb04c94ea9c?q=80&w=600",
        ),
    ],
    "vehiculos": [
        (
            "Base Soporte Celular para Moto",
            "Con carga USB y sujeción firme. Subcategoría: Motocicletas",
            35000,
            "https://images.unsplash.com/photo-1558981806-ec527fa84c39?q=80&w=600",
        ),
        (
            "Casco Certificado DOT talla M",
            "Semi-integral negro mate, un mes de uso. Subcategoría: Seguridad",
            160000,
            "https://images.unsplash.com/photo-1563063539-75bd7c8b4ce0?q=80&w=600",
        ),
        (
            "Crema Encapsuladora Brilladora Auto",
            "Quita rayones superficiales e hidrata la pintura. Subcategoría: Autopartes",
            25000,
            "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?q=80&w=600",
        ),
        (
            "Guantes Impermeables para Moto",
            "Con protecciones en nudillos. Indispensables en lluvia. Subcategoría: Ropa de moto",
            40000,
            "https://images.unsplash.com/photo-1628124978809-5c74233519c7?q=80&w=600",
        ),
        (
            "Candado de Disco con Alarma Moto",
            "Sensible a la vibración, batería buena. Subcategoría: Seguridad",
            45000,
            "https://images.unsplash.com/photo-1616036740257-9449ea1f6605?q=80&w=600",
        ),
        (
            "Pito Bocina Corneta de Carro",
            "Muy potente para hacerse escuchar. Subcategoría: Eléctrico",
            30000,
            "https://images.unsplash.com/photo-1567115843477-743a34f828a2?q=80&w=600",
        ),
        (
            "Cubierta Funda Impermeable para Carro",
            "Evita el sol e intemperie. Tamaño Sedan Talla L. Subcategoría: Accesorios",
            75000,
            "https://images.unsplash.com/photo-1580273916550-e323be2ae537?q=80&w=600",
        ),
        (
            "Impermeable 2 Piezas Reflectivo",
            "Excelente calidad. Cero filtraciones. Subcategoría: Ropa de moto",
            60000,
            "https://images.unsplash.com/photo-1615560127264-52d3bf305a46?q=80&w=600",
        ),
        (
            "Tapetes de Caucho 4 piezas Coche",
            "Universales y de fácil lavado. Subcategoría: Interiores",
            38000,
            "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=600",
        ),
        (
            "Kit Pinchazos Llantas Sellomathic",
            "Trae los tarugos y herramientas necesarias. Cúbrete emergencias. Subcategoría: Herramientas",
            15000,
            "https://images.unsplash.com/photo-1506469717960-433cebe3f181?q=80&w=600",
        ),
    ],
}


async def main():
    async with AsyncSessionLocal() as db:
        # Check if there are users, create a default vendor user if necessary
        result = await db.execute(text("SELECT id FROM users LIMIT 1"))
        user_row = result.fetchone()

        if not user_row:
            user_id = str(uuid4())
            await db.execute(
                text(f"""
                INSERT INTO users (id, name, email, role, vendor_status) 
                VALUES ('{user_id}', 'Vendedor Bot', 'bot@veramarket.com', 'vendedor', 'approved')
            """)
            )
            await db.commit()
            logger.info("Creado usuario vendedor fantasma.")
        else:
            user_id = str(user_row[0])
            logger.info("Se usará el primer usuario de la DB como vendedor.")

        # --- Limpieza de tabla de productos y typesense (opcional pero lo recomendaron en prompt) ---
        await db.execute(text("TRUNCATE TABLE products CASCADE"))
        await db.commit()

        # Eliminar todos los docs de typesense
        # Ya que _get_client puede fallar desde asincrono puro, lo llamamos indirectamente
        import app.services.typesense_service as ts

        try:
            client = ts._get_client()
            client.collections[settings.TYPESENSE_COLLECTION_PRODUCTS].delete()
            logger.info("Indice anterior Typesense destruido.")
            await ts.ensure_products_collection()
            logger.info("Indice Typesense recreado en limpio.")
        except Exception as e:
            logger.warning(f"Error reseteando Typesense: {e}")

        # --- Generar Productos ---
        product_count = 0

        # Un arreglo global para evitar problemas si los keys no existen
        for cat_name, items in CATALOG_SEED.items():
            for name, desc, price, img_url in items:
                # Inserción en PosgtreSQL usando ORM (Product)
                prod_id = uuid4()
                p = Product(
                    id=prod_id,
                    seller_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                    name=name,
                    description=desc,
                    price=price,
                    category=cat_name,
                    image_urls=[img_url],
                    is_active=True,
                )

                # Asignar manualmente seller_id por si hay problemas de parseo:
                p.seller_id = user_id

                db.add(p)
                product_count += 1

                # Insertar/Update en Typesense
                await db.flush()  # asura el estado del objeto
                try:
                    await upsert_product_document(db, p)
                except Exception as ex:
                    logger.warning(f"No se pudo indexar {p.name} en Typesense: {ex}")

        await db.commit()
        logger.info(
            f"ÉXITO: Se insertaron e indexaron {product_count} productos exitosamente."
        )


if __name__ == "__main__":
    asyncio.run(main())
