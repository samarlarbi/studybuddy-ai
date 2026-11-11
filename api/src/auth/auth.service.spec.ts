import { ConflictException, UnauthorizedException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  const users = { findByEmail: jest.fn(), create: jest.fn() };
  const jwt = { sign: jest.fn().mockReturnValue('token') };
  const service = new AuthService(users as any, jwt as any);

  beforeEach(() => jest.clearAllMocks());

  it('rejects a duplicate email', async () => {
    users.findByEmail.mockResolvedValue({ id: '1' });
    await expect(
      service.register({ email: 'a@a.com', password: 'password123' }),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('rejects a wrong password', async () => {
    users.findByEmail.mockResolvedValue({
      id: '1',
      email: 'a@a.com',
      passwordHash: await bcrypt.hash('right-password', 10),
    });
    await expect(
      service.login({ email: 'a@a.com', password: 'wrong-password' }),
    ).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it('returns a token on valid login', async () => {
    users.findByEmail.mockResolvedValue({
      id: '1',
      email: 'a@a.com',
      passwordHash: await bcrypt.hash('password123', 10),
    });
    await expect(
      service.login({ email: 'a@a.com', password: 'password123' }),
    ).resolves.toEqual({ accessToken: 'token' });
  });
});