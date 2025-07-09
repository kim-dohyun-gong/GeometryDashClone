import pygame
import sys
import random
import math
#dkdkdkㄴㅇㄹhhh
# 게임 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("지오메트리 대쉬 클론")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# 게임 상수
GRAVITY = 0.8
JUMP_FORCE = -15
GROUND_HEIGHT = 100
PLAYER_SIZE = 40
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 60
BACKGROUND_SPEED = 2
GROUND_SPEED = 5
OBSTACLE_SPEED = 5

# 폰트 설정
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# 장애물 타입
OBSTACLE_TYPES = {
    'SPIKE': 0,
    'PLATFORM': 1,
    'PLATFORM_WITH_SPIKE': 2
}


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-2, -0.5)  # 뒤쪽으로 이동
        self.vel_y = random.uniform(-2, 2)  # 위아래로 퍼짐
        self.size = random.uniform(1, 3)  # 작은 크기
        self.life = random.uniform(20, 40)  # 수명
        self.max_life = self.life
        self.color = random.choice([BLUE, CYAN, WHITE, (100, 150, 255)])

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

        # 중력 효과 (아주 약하게)
        self.vel_y += 0.05

        # 크기 감소
        self.size *= 0.98

    def draw(self, screen):
        if self.life > 0 and self.size > 0.1:
            # 투명도 계산
            alpha = int(255 * (self.life / self.max_life))
            alpha = max(0, min(255, alpha))

            # 파티클 그리기
            if alpha > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

    def is_dead(self):
        return self.life <= 0 or self.size <= 0.1


class Player:
    def __init__(self):
        self.x = 150
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.on_ground = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.rotation = 0
        self.rotation_speed = 0
        self.particles = []
        self.particle_timer = 0

        # 이미지 로드
        self.image = None
        self.original_image = None
        self.use_image = False
        try:
            self.original_image = pygame.image.load("임시assets/avatar.png")
            self.original_image = pygame.transform.scale(self.original_image, (PLAYER_SIZE, PLAYER_SIZE))
            self.image = self.original_image.copy()
            self.use_image = True
        except pygame.error:
            self.use_image = False
            print("이미지 파일을 찾을 수 없습니다. 기본 도형을 사용합니다.")

    def update(self):
        if not self.on_ground:
            self.vel_y += GRAVITY

        self.y += self.vel_y

        if not self.on_ground:
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0

            if self.use_image and self.original_image:
                self.image = pygame.transform.rotate(self.original_image, -self.rotation)

        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.vel_y = 0
            self.on_ground = True
            self.rotation = 0
            self.rotation_speed = 0
            if self.use_image and self.original_image:
                self.image = self.original_image.copy()
        else:
            self.on_ground = False

        if self.y < 0:
            self.y = 0
            self.vel_y = 0

        self.rect.y = self.y

        # 파티클 생성 (왼쪽 아래 모서리에서)
        self.particle_timer += 1
        if self.particle_timer >= 3:  # 3프레임마다 파티클 생성
            particle_x = self.x + 2  # 왼쪽 모서리에서 약간 안쪽
            particle_y = self.y + self.height - 5  # 아래쪽 모서리에서 약간 위
            self.particles.append(Particle(particle_x, particle_y))
            self.particle_timer = 0

        # 파티클 업데이트
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.rotation_speed = 12

    def move_up(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.rotation_speed = 12

    def draw(self, screen):
        # 파티클 먼저 그리기 (플레이어 뒤에)
        for particle in self.particles:
            particle.draw(screen)

        # 플레이어 그리기
        if self.use_image and self.image:
            image_rect = self.image.get_rect()
            image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            screen.blit(self.image, image_rect)
        else:
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            half_size = self.width // 2
            corners = [
                (-half_size, -half_size),
                (half_size, -half_size),
                (half_size, half_size),
                (-half_size, half_size)
            ]

            rotated_corners = []
            angle_rad = math.radians(self.rotation)
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)

            for corner_x, corner_y in corners:
                new_x = corner_x * cos_angle - corner_y * sin_angle
                new_y = corner_x * sin_angle + corner_y * cos_angle
                rotated_corners.append((center_x + new_x, center_y + new_y))

            pygame.draw.polygon(screen, BLUE, rotated_corners)


class Obstacle:
    def __init__(self, x, obstacle_type=None):
        self.x = x
        self.obstacle_type = obstacle_type if obstacle_type is not None else random.choice(
            list(OBSTACLE_TYPES.values()))
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.rotation = 0
        self.rotation_speed = 0

        # 타입별 속성 설정
        self.setup_obstacle_properties()

        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # 플랫폼용 충돌 박스들 (왼쪽, 오른쪽 끝만 위험)
        self.collision_rects = []
        if self.obstacle_type == OBSTACLE_TYPES['PLATFORM']:
            # 왼쪽 끝 (세로 부분)
            self.collision_rects.append(pygame.Rect(self.x, self.y, 10, self.height))
            # 오른쪽 끝 (세로 부분)
            self.collision_rects.append(pygame.Rect(self.x + self.width - 10, self.y, 10, self.height))
        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']:
            # 왼쪽 끝 (세로 부분)
            self.collision_rects.append(pygame.Rect(self.x, self.y, 10, self.height))
            # 오른쪽 끝 (세로 부분)
            self.collision_rects.append(pygame.Rect(self.x + self.width - 10, self.y, 10, self.height))
            # 위의 스파이크
            spike_x = self.x + self.width // 2 - 15
            spike_y = self.y - 40
            self.collision_rects.append(pygame.Rect(spike_x, spike_y, 30, 40))
        else:
            # 일반 장애물은 전체가 충돌 영역
            self.collision_rects.append(self.rect)

    def setup_obstacle_properties(self):
        if self.obstacle_type == OBSTACLE_TYPES['SPIKE']:
            self.color = RED
            self.width = 30
            self.height = 60

        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM']:
            self.color = GREEN
            self.width = 120  # 더 긴 플랫폼
            self.height = 20
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 80  # 점프 가능한 높이

        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']:
            self.color = GREEN
            self.width = 120  # 더 긴 플랫폼
            self.height = 20
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 80  # 점프 가능한 높이

    def update(self):
        self.x -= OBSTACLE_SPEED
        self.rect.x = self.x

        # 충돌 박스들도 업데이트
        if self.obstacle_type == OBSTACLE_TYPES['PLATFORM']:
            self.collision_rects[0].x = self.x  # 왼쪽 끝
            self.collision_rects[1].x = self.x + self.width - 10  # 오른쪽 끝
        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']:
            self.collision_rects[0].x = self.x  # 왼쪽 끝
            self.collision_rects[1].x = self.x + self.width - 10  # 오른쪽 끝
            self.collision_rects[2].x = self.x + self.width // 2 - 15  # 스파이크
        else:
            self.collision_rects[0].x = self.x

        # 회전하는 장애물 업데이트
        if self.rotation_speed != 0:
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0

    def draw(self, screen):
        if self.obstacle_type == OBSTACLE_TYPES['SPIKE']:
            # 삼각형 스파이크
            points = [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(screen, self.color, points)

        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM']:
            # 직사각형 플랫폼
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

            # 위험한 끝 부분 표시 (빨간색으로 강조)
            pygame.draw.rect(screen, RED, (self.x, self.y, 10, self.height))
            pygame.draw.rect(screen, RED, (self.x + self.width - 10, self.y, 10, self.height))

        elif self.obstacle_type == OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']:
            # 직사각형 플랫폼
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

            # 위험한 끝 부분 표시 (빨간색으로 강조)
            pygame.draw.rect(screen, RED, (self.x, self.y, 10, self.height))
            pygame.draw.rect(screen, RED, (self.x + self.width - 10, self.y, 10, self.height))

            # 플랫폼 위의 스파이크 (중앙에 위치)
            spike_x = self.x + self.width // 2 - 15
            spike_y = self.y - 40
            spike_points = [
                (spike_x + 15, spike_y),
                (spike_x, spike_y + 40),
                (spike_x + 30, spike_y + 40)
            ]
            pygame.draw.polygon(screen, RED, spike_points)

        # 디버그용 충돌 박스 그리기 (옵션)
        # for rect in self.collision_rects:
        #     pygame.draw.rect(screen, (255, 0, 0, 50), rect, 1)

    def is_off_screen(self):
        return self.x + self.width < 0


class Background:
    def __init__(self):
        self.bg_x1 = 0
        self.bg_x2 = SCREEN_WIDTH
        self.ground_x1 = 0
        self.ground_x2 = SCREEN_WIDTH
        self.background_image = None
        self.ground_image = None
        self.use_background_image = False
        self.use_ground_image = False

        try:
            original_bg = pygame.image.load("임시assets/bg.png")
            self.background_image = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
            del original_bg
            self.use_background_image = True
            print("배경 이미지 로드 완료")
        except pygame.error:
            print("배경 이미지를 찾을 수 없습니다. 기본 배경을 사용합니다.")
            self.use_background_image = False

        try:
            original_ground = pygame.image.load("임시assets/bottom.png")
            self.ground_image = pygame.transform.scale(original_ground, (SCREEN_WIDTH, GROUND_HEIGHT))
            del original_ground
            self.use_ground_image = True
            print("바닥 이미지 로드 완료")
        except pygame.error:
            print("바닥 이미지를 찾을 수 없습니다. 기본 바닥을 사용합니다.")
            self.use_ground_image = False

    def update(self):
        self.bg_x1 -= BACKGROUND_SPEED
        self.bg_x2 -= BACKGROUND_SPEED

        if self.bg_x1 <= -SCREEN_WIDTH:
            self.bg_x1 = SCREEN_WIDTH
        if self.bg_x2 <= -SCREEN_WIDTH:
            self.bg_x2 = SCREEN_WIDTH

        self.ground_x1 -= GROUND_SPEED
        self.ground_x2 -= GROUND_SPEED

        if self.ground_x1 <= -SCREEN_WIDTH:
            self.ground_x1 = SCREEN_WIDTH
        if self.ground_x2 <= -SCREEN_WIDTH:
            self.ground_x2 = SCREEN_WIDTH

    def draw(self, screen):
        if self.use_background_image and self.background_image:
            screen.blit(self.background_image, (self.bg_x1, 0))
            screen.blit(self.background_image, (self.bg_x2, 0))
        else:
            for i in range(SCREEN_HEIGHT - GROUND_HEIGHT):
                color_intensity = 135 + int(120 * (i / (SCREEN_HEIGHT - GROUND_HEIGHT)))
                if color_intensity > 255:
                    color_intensity = 255
                pygame.draw.line(screen, (color_intensity, color_intensity, 255), (0, i), (SCREEN_WIDTH, i))

        if self.use_ground_image and self.ground_image:
            screen.blit(self.ground_image, (self.ground_x1, SCREEN_HEIGHT - GROUND_HEIGHT))
            screen.blit(self.ground_image, (self.ground_x2, SCREEN_HEIGHT - GROUND_HEIGHT))
        else:
            ground_rect1 = pygame.Rect(self.ground_x1, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
            ground_rect2 = pygame.Rect(self.ground_x2, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
            pygame.draw.rect(screen, GREEN, ground_rect1)
            pygame.draw.rect(screen, GREEN, ground_rect2)

            for x in range(int(self.ground_x1), int(self.ground_x1) + SCREEN_WIDTH + 50, 50):
                if x >= -50 and x <= SCREEN_WIDTH:
                    pygame.draw.line(screen, DARK_GRAY, (x, SCREEN_HEIGHT - GROUND_HEIGHT), (x, SCREEN_HEIGHT), 3)
            for x in range(int(self.ground_x2), int(self.ground_x2) + SCREEN_WIDTH + 50, 50):
                if x >= -50 and x <= SCREEN_WIDTH:
                    pygame.draw.line(screen, DARK_GRAY, (x, SCREEN_HEIGHT - GROUND_HEIGHT), (x, SCREEN_HEIGHT), 3)


class GameOverScreen:
    def __init__(self):
        self.restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)

    def draw(self, screen, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)

        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        pygame.draw.rect(screen, GRAY, self.restart_button)
        pygame.draw.rect(screen, WHITE, self.restart_button, 2)
        restart_text = font_medium.render("Restart?", True, WHITE)
        restart_rect = restart_text.get_rect(center=self.restart_button.center)
        screen.blit(restart_text, restart_rect)

    def handle_click(self, pos):
        return self.restart_button.collidepoint(pos)


class ObstaclePattern:
    """장애물 패턴을 관리하는 클래스"""

    def __init__(self):
        self.patterns = [
            # 쉬운 패턴들 (초반용)
            # 패턴 1: 기본 스파이크
            [(0, OBSTACLE_TYPES['SPIKE'])],

            # 패턴 2: 플랫폼 단독
            [(0, OBSTACLE_TYPES['PLATFORM'])],

            # 패턴 3: 스파이크 2개 (충분한 간격)
            [(0, OBSTACLE_TYPES['SPIKE']), (120, OBSTACLE_TYPES['SPIKE'])],

            # 패턴 4: 스파이크 후 플랫폼 (충분한 간격)
            [(0, OBSTACLE_TYPES['SPIKE']), (140, OBSTACLE_TYPES['PLATFORM'])],

            # 패턴 5: 플랫폼 후 스파이크 (충분한 간격)
            [(0, OBSTACLE_TYPES['PLATFORM']), (160, OBSTACLE_TYPES['SPIKE'])],

            # 중간 난이도 패턴들
            # 패턴 6: 플랫폼 + 스파이크
            [(0, OBSTACLE_TYPES['PLATFORM_WITH_SPIKE'])],

            # 패턴 7: 플랫폼 + 스파이크 후 단독 스파이크
            [(0, OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']), (180, OBSTACLE_TYPES['SPIKE'])],

            # 패턴 8: 연속 플랫폼
            [(0, OBSTACLE_TYPES['PLATFORM']), (140, OBSTACLE_TYPES['PLATFORM'])],

            # 어려운 패턴들 (후반용)
            # 패턴 9: 스파이크 - 플랫폼 - 스파이크 (넓은 간격)
            [(0, OBSTACLE_TYPES['SPIKE']), (120, OBSTACLE_TYPES['PLATFORM']), (260, OBSTACLE_TYPES['SPIKE'])],

            # 패턴 10: 복합 패턴 (넓은 간격)
            [(0, OBSTACLE_TYPES['SPIKE']), (140, OBSTACLE_TYPES['PLATFORM_WITH_SPIKE']),
             (300, OBSTACLE_TYPES['SPIKE'])],
        ]

        self.current_pattern = 0
        self.pattern_position = 0
        self.obstacles_in_pattern = []

    def get_next_pattern(self, score):
        """점수에 따라 패턴을 선택"""
        if score < 3:
            # 초반엔 매우 쉬운 패턴 (단독 장애물만)
            return random.choice(self.patterns[:2])
        elif score < 8:
            # 중반엔 간단한 패턴
            return random.choice(self.patterns[:5])
        elif score < 15:
            # 중후반엔 중간 난이도 패턴
            return random.choice(self.patterns[:8])
        else:
            # 후반엔 어려운 패턴 (하지만 3연속 스파이크는 제외)
            return random.choice(self.patterns[:10])


class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.background = Background()
        self.game_over_screen = GameOverScreen()
        self.obstacle_pattern = ObstaclePattern()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_delay = 120  # 더 긴 간격으로 시작
        self.current_pattern = []
        self.pattern_spawn_index = 0

    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.background = Background()
        self.obstacle_pattern = ObstaclePattern()
        self.score = 0
        self.game_over = False
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_delay = 120  # 초기 간격 복구
        self.current_pattern = []
        self.pattern_spawn_index = 0

    def spawn_obstacle(self):
        if self.obstacle_spawn_timer <= 0:
            # 새 패턴 시작
            if not self.current_pattern:
                self.current_pattern = self.obstacle_pattern.get_next_pattern(self.score)
                self.pattern_spawn_index = 0

            # 현재 패턴에서 장애물 생성
            if self.pattern_spawn_index < len(self.current_pattern):
                offset, obstacle_type = self.current_pattern[self.pattern_spawn_index]
                self.obstacles.append(Obstacle(SCREEN_WIDTH + offset, obstacle_type))
                self.pattern_spawn_index += 1

                # 패턴 내 다음 장애물까지의 딜레이
                self.obstacle_spawn_timer = 20
            else:
                # 패턴 완료, 다음 패턴까지 대기
                self.current_pattern = []
                self.obstacle_spawn_timer = self.obstacle_spawn_delay

                # 점수에 따라 난이도 증가 (하지만 너무 빠르지 않게)
                if self.score > 5:
                    self.obstacle_spawn_delay = max(90, 150 - self.score * 2)
        else:
            self.obstacle_spawn_timer -= 1

    def update(self):
        if not self.game_over:
            self.player.update()
            self.background.update()
            self.spawn_obstacle()

            for obstacle in self.obstacles[:]:
                obstacle.update()

                # 충돌 체크 - 각 장애물의 충돌 박스들과 체크
                for collision_rect in obstacle.collision_rects:
                    if self.player.rect.colliderect(collision_rect):
                        self.game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score
                        break

                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
                    self.score += 1

    def draw(self, screen):
        self.background.draw(screen)
        self.player.draw(screen)

        for obstacle in self.obstacles:
            obstacle.draw(screen)

        self.draw_ui(screen)

        if self.game_over:
            self.game_over_screen.draw(screen, self.score)

    def draw_ui(self, screen):
        score_text = font_medium.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        high_score_text = font_small.render(f"High Score: {self.high_score}", True, BLACK)
        screen.blit(high_score_text, (10, 50))

        if self.score == 0 and not self.game_over:
            help_text = font_small.render("Press UP arrow or SPACE to jump!", True, BLACK)
            help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(help_text, help_rect)

    def handle_click(self, pos):
        if self.game_over:
            if self.game_over_screen.handle_click(pos):
                self.reset_game()


def main():
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game.game_over:
                        game.player.jump()
                elif event.key == pygame.K_UP:
                    if not game.game_over:
                        game.player.move_up()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not game.game_over:
                        game.player.jump()
                    else:
                        game.handle_click(event.pos)

        game.update()

        screen.fill(WHITE)
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()