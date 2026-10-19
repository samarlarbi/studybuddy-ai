import { ConflictException, Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from '../users/users.service';
import { AuthDto } from './auth.dto';

@Injectable()
export class AuthService {
  constructor(private users: UsersService, private jwt: JwtService) {}

  async register(dto: AuthDto) {
    if (await this.users.findByEmail(dto.email)) {
      throw new ConflictException('Email already used');
    }
    const hash = await bcrypt.hash(dto.password, 10);
    const user = await this.users.create(dto.email, hash);
    return this.token(user.id, user.email);
  }

  async login(dto: AuthDto) {
    const user = await this.users.findByEmail(dto.email);
    if (!user || !(await bcrypt.compare(dto.password, user.passwordHash))) {
      throw new UnauthorizedException('Invalid credentials');
    }
    return this.token(user.id, user.email);
  }

  private token(id: string, email: string) {
    return { accessToken: this.jwt.sign({ sub: id, email }) };
  }
}