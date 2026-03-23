require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { createClient } = require('redis');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const REDIS_HOST = process.env.REDIS_HOST || 'localhost';
const REDIS_PORT = process.env.REDIS_PORT || 6379;

app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Inicializar y conectar cliente Redis
const redisClient = createClient({
    url: `redis://${REDIS_HOST}:${REDIS_PORT}`
});

redisClient.on('error', (err) => console.log('Redis Client Error', err));

// Conexión asíncrona y robusta
(async () => {
    try {
        await redisClient.connect();
        console.log('Visualizer conectado a Redis exitosamente.');
    } catch (e) {
        console.error('Fallo al conectar con Redis', e);
    }
})();

/**
 * GET /api/ranking
 * Obtiene el top N de palabras más frecuentes en tiempo real.
 * @query {number} top - Limita la cantidad de resultados (por defecto 20).
 */
app.get('/api/ranking', async (req, res) => {
    try {
        const topN = parseInt(req.query.top, 10) || 20;
        
        // ZREVRANGEBYSCORE no, ZREVRANGE devuelve de mayor a menor score desde el índice 0 hasta topN - 1
        const stopIndex = topN - 1 < 0 ? 0 : topN - 1;
        const result = await redisClient.zRangeWithScores('word_ranking', 0, stopIndex, { REV: true });
        
        // Formatear al array legible de { word: string, score: number }
        const ranking = result.map(item => ({
            word: item.value,
            score: item.score
        }));
        
        res.json({ ranking });
    } catch (error) {
        console.error('Error procesando request /api/ranking:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(PORT, () => {
    console.log(`Visualizer corriendo en el puerto ${PORT}`);
});
