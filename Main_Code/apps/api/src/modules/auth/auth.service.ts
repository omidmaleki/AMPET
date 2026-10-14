import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(private readonly jwtService: JwtService) {}

  createAccessToken(userId: string, role: string, sessionId: string): string {
    return this.jwtService.sign(
      { sub: userId, role, sid: sessionId },
      { expiresIn: '15m' },
    );
  }

  createAdminAccessToken(userId: string, sessionId: string): string {
    return this.jwtService.sign(
      { sub: userId, role: 'admin', sid: sessionId },
      { expiresIn: '10m' },
    );
  }

  createRefreshToken(sessionId: string): string {
    // ۳۰ روزه چرخشی — در هر refresh ردیف sessions به‌روزرسانی می‌شود
    return this.jwtService.sign({ sid: sessionId, type: 'refresh' }, { expiresIn: '30d' });
  }

  verifyRefresh(token: string): { sid: string; type: string } {
    return this.jwtService.verify(token) as { sid: string; type: string };
  }
}
