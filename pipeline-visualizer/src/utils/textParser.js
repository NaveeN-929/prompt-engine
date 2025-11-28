/**
 * Text Parser Utilities
 * Parse LLM output into structured insights and recommendations
 */

/**
 * Parse insights and recommendations from LLM output
 */
export const parseOutput = (text) => {
  if (!text || typeof text !== 'string') {
    return { insights: [], recommendations: [] };
  }

  // Step 1: Convert literal \n to actual newlines
  let cleanText = text.replace(/\\n/g, '\n');

  // Step 2: Extract SECTION 1 (Insights) and SECTION 2 (Recommendations)
  const insightSection = extractSection(cleanText, 'SECTION 1', 'INSIGHTS?');
  const recommendSection = extractSection(cleanText, 'SECTION 2', 'RECOMMENDATIONS?');

  // Step 3: Parse each section into bullet points
  const insights = parseBulletPoints(insightSection, 'Insight');
  const recommendations = parseBulletPoints(recommendSection, 'Recommendation');

  return { insights, recommendations };
};

/**
 * Extract a section from text
 */
const extractSection = (text, sectionNum, sectionName) => {
  const pattern = new RegExp(
    `===\\s*${sectionNum}:\\s*${sectionName}\\s*===\\s*([\\s\\S]*?)(?====\\s*SECTION|===\\s*ANALYSIS|$)`,
    'i'
  );
  const match = text.match(pattern);
  return match ? match[1].trim() : '';
};

/**
 * Parse text into bullet points
 */
const parseBulletPoints = (text, itemPrefix = 'Insight') => {
  if (!text) return [];

  const items = [];

  // Split by double newlines first
  const segments = text.split(/\n\n+/);

  for (const segment of segments) {
    const trimmed = segment.trim();
    if (!trimmed || trimmed.length < 10) continue;

    // Check if this segment has the "Insight X:" or "Recommendation X:" prefix
    const prefixPattern = new RegExp(`^${itemPrefix}\\s*\\d+:\\s*(.+)$`, 'i');
    const match = trimmed.match(prefixPattern);

    if (match) {
      // Has prefix - extract the content after the colon
      const content = cleanupText(match[1]);
      if (content.length > 0 && isValidBulletPoint(content)) {
        items.push(content);
      }
    } else {
      // No prefix - use the whole segment if it's valid
      const content = cleanupText(trimmed);
      if (content.length > 0 && isValidBulletPoint(content)) {
        items.push(content);
      }
    }
  }

  return items;
};

/**
 * Clean up text by removing unwanted characters and metadata
 */
const cleanupText = (text) => {
  return text
    // Remove multiple spaces
    .replace(/\s+/g, ' ')
    // Remove extra newlines
    .replace(/\n+/g, ' ')
    // Trim
    .trim();
};

/**
 * Check if text is a valid bullet point
 */
const isValidBulletPoint = (text) => {
  if (!text || text.length < 15) return false;
  
  // Exclude metadata lines
  const excludePatterns = [
    /^===.*===/,
    /^Generated through/i,
    /^Enhanced with/i,
    /^Business context/i,
    /^No fallback/i,
    /^ANALYSIS METADATA/i,
    /^SECTION \d+/i
  ];

  return !excludePatterns.some(pattern => pattern.test(text));
};

/**
 * Format quality score as percentage
 */
export const formatQualityScore = (score) => {
  if (typeof score !== 'number') return 'N/A';
  return `${(score * 100).toFixed(1)}%`;
};

/**
 * Get quality level label and color
 */
export const getQualityLevel = (score) => {
  if (score >= 0.95) return { label: 'Exemplary', color: 'success' };
  if (score >= 0.80) return { label: 'High Quality', color: 'success' };
  if (score >= 0.65) return { label: 'Acceptable', color: 'warning' };
  return { label: 'Poor', color: 'error' };
};

export default {
  parseOutput,
  formatQualityScore,
  getQualityLevel
};
