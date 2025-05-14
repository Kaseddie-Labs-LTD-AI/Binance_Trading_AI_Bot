import ai from './index.js';

// Define an AI function to process market analysis
export const getMarketInsights = async (query) => {
    try {
        const { text } = await ai.generate(`Analyze the crypto market: ${query}`);
        return text;
    } catch (error) {
        console.error('AI analysis failed:', error);
        return 'Error processing request.';
    }
};