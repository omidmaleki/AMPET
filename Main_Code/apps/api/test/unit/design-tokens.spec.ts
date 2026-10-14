import { existsSync, readFileSync } from 'fs';
import * as path from 'path';

/**
 * design/color_tokens_match_contract_hex (SP-00 §4 + M-00.7)
 * قفل رنگ‌ها/فونت قرارداد بین Dart و CSS — بدون نیاز به Flutter SDK.
 */
const CONTRACT = {
  primary: '#0F5D4A',
  accent: '#D4AF37',
  text: '#111827',
  surface: '#F9FAFB',
};

const root = path.resolve(__dirname, '..', '..', '..', '..'); // apps/api/test/unit → repo root
const dartTokens = path.join(root, 'apps', 'app', 'lib', 'design', 'tokens.dart');
const cssTokens = path.join(root, 'apps', 'web-admin', 'styles', 'tokens.css');

describe('Design tokens match contract (SP-00 §4)', () => {
  it('both token files exist', () => {
    expect(existsSync(dartTokens)).toBe(true);
    expect(existsSync(cssTokens)).toBe(true);
  });

  it('design/color_tokens_match_contract_hex', () => {
    for (const file of [dartTokens, cssTokens]) {
      const content = readFileSync(file, 'utf8').toUpperCase();
      for (const hex of Object.values(CONTRACT)) {
        expect(content).toContain(hex.toUpperCase());
      }
      expect(content).toContain('VAZIRMATN');
    }
  });
});
