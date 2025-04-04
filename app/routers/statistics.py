from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from ..utils.auth import get_current_user
import json

router = APIRouter(
    prefix="/hero/statistics",
    tags=["Statistics"]
)

@router.get("/{user_id}")
async def get_user_statistics(
    user_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 종합 통계 데이터를 가져옵니다."""
    # 현재 인증된 사용자가 요청된 사용자 ID와 일치하는지 확인
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 통계 정보에 접근할 권한이 없습니다."
        )
    
    # 현재 유저의 Hero 정보 가져오기
    hero_result = await db.execute(
        select(models.Hero).filter(models.Hero.user_id == user_id)
    )
    hero = hero_result.scalar_one_or_none()
    
    if not hero:
        raise HTTPException(
            status_code=404,
            detail="영웅 정보를 찾을 수 없습니다."
        )
    
    # 총 퀘스트 수와 완료한 퀘스트 수 계산
    total_quests_result = await db.execute(
        select(func.count()).select_from(models.Quest).filter(
            models.Quest.user_id == user_id
        )
    )
    total_quests = total_quests_result.scalar_one() or 0
    
    completed_quests_result = await db.execute(
        select(func.count()).select_from(models.Quest).filter(
            models.Quest.user_id == user_id,
            models.Quest.finish == True
        )
    )
    completed_quests = completed_quests_result.scalar_one() or 0
    
    # 경험치는 현재 레벨 기준으로 계산 (예시)
    total_xp = hero.hero_level * 1000
    
    # 평균 일일 활동 시간 계산 (최근 7일)
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    
    activity_result = await db.execute(
        select(func.avg(models.Quest.progress_time)).filter(
            models.Quest.user_id == user_id,
            models.Quest.start_time >= seven_days_ago
        )
    )
    avg_daily_activity = activity_result.scalar_one() or 0
    avg_daily_activity_hours = round(avg_daily_activity / 3600, 1)  # 초 단위를 시간으로 변환
    
    # 연속 달성 일수 계산
    streak_days = await _calculate_streak_days(db, user_id)
    
    # 월간 목표 달성률 계산
    monthly_goal_percentage = await _calculate_monthly_goal_percentage(db, user_id)
    
    # 레벨업 진행률 계산
    level_progress_percentage = await _calculate_level_progress(db, user_id, hero.hero_level)
    
    # 캘린더 데이터 생성
    calendar_data = await _get_calendar_data(db, user_id)
    
    # 태그 통계 데이터 생성
    tags_data = await _get_tag_statistics(db, user_id)
    
    # 주간 활동 데이터 생성
    weekly_data = await _get_weekly_activity(db, user_id)
    
    # 스탯 정보 가져오기
    stats = await _get_user_stats(db, user_id)
    
    return {
        "summary": {
            "totalQuests": total_quests,
            "completedQuests": completed_quests,
            "totalXp": total_xp,
            "avg_daily_activity": avg_daily_activity_hours,
            "streakDays": streak_days,
            "monthly_goal_percentage": monthly_goal_percentage,
            "level_progress_percentage": level_progress_percentage
        },
        "calendar": calendar_data,
        "tags": tags_data,
        "weekly": weekly_data,
        "stats": stats  # 스탯 정보 추가
    }

@router.get("/{user_id}/period")
async def get_period_statistics(
    user_id: int, 
    type: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """특정 기간(주간, 월간, 연간)의 활동 통계를 가져옵니다."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 통계 정보에 접근할 권한이 없습니다."
        )
    
    now = datetime.now()
    
    if type == 'week':
        start_date = now - timedelta(days=7)
        period_data = await _get_weekly_activity(db, user_id, start_date, now)
    elif type == 'month':
        start_date = now - timedelta(days=30)
        period_data = await _get_monthly_activity(db, user_id, start_date, now)
    elif type == 'year':
        start_date = now - timedelta(days=365)
        period_data = await _get_yearly_activity(db, user_id, start_date, now)
    else:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 기간 타입입니다. 'week', 'month', 'year' 중 하나를 사용하세요."
        )
    
    return period_data

@router.get("/{user_id}/tags")
async def get_tag_statistics_endpoint(
    user_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 태그별 통계를 가져옵니다."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="다른 사용자의 태그 통계에 접근할 권한이 없습니다."
        )
    
    tags_data = await _get_tag_statistics(db, user_id)
    return tags_data

# 도우미 함수들

async def _get_user_stats(db: AsyncSession, user_id: int):
    """사용자의 스탯 정보를 계산합니다."""
    try:
        # 사용자의 완료된 퀘스트 정보 가져오기
        quest_result = await db.execute(
            select(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True
            )
        )
        completed_quests = quest_result.scalars().all()
        
        # 기본 스탯 값 설정
        stats = {
            "strength": 10,  # 힘
            "intelligence": 10,  # 지능
            "vitality": 10,  # 체력
            "dexterity": 10,  # 손재주
            "endurance": 10,  # 인내력
        }
        
        # 완료된 퀘스트의 태그에 따라 스탯 증가
        for quest in completed_quests:
            try:
                if quest.tag:
                    tags = json.loads(quest.tag) if isinstance(quest.tag, str) else quest.tag
                    if not isinstance(tags, list):
                        continue
                        
                    for tag in tags:
                        # 태그에 따른 스탯 증가
                        if tag == "운동 및 스포츠":
                            stats["strength"] += 2
                            stats["vitality"] += 2
                        elif tag == "공부":
                            stats["intelligence"] += 3
                        elif tag == "자기개발":
                            stats["intelligence"] += 2
                            stats["dexterity"] += 1
                        elif tag == "취미":
                            stats["dexterity"] += 3
                        elif tag == "명상 및 스트레칭":
                            stats["vitality"] += 1
                            stats["endurance"] += 2
                        else:  # 기타
                            # 모든 스탯에 균등하게 추가
                            for stat in stats:
                                stats[stat] += 0.5
            except (json.JSONDecodeError, TypeError):
                continue
        
        # 스탯이 너무 높지 않도록 최대값 설정
        for stat in stats:
            stats[stat] = min(round(stats[stat]), 100)
        
        return stats
        
    except Exception as e:
        # 에러 로깅
        print(f"Error in _get_user_stats: {e}")
        # 기본 스탯 반환
        return {
            "strength": 10,
            "intelligence": 10,
            "vitality": 10,
            "dexterity": 10,
            "endurance": 10,
        }
    
async def _calculate_streak_days(db: AsyncSession, user_id: int):
    """사용자의 연속 달성 일수를 계산합니다."""
    try:
        now = datetime.now().date()
        
        # 최대 30일 전까지의 데이터 확인
        streak = 0
        current_date = now
        
        for _ in range(30):  # 최대 30일 확인
            # 해당 날짜에 완료된 퀘스트가 있는지 확인
            date_result = await db.execute(
                select(models.Quest).filter(
                    models.Quest.user_id == user_id,
                    models.Quest.finish == True,
                    func.date(models.Quest.finish_time) == current_date
                )
            )
            completed_quests = date_result.scalars().all()
            
            if not completed_quests:
                break  # 완료된 퀘스트가 없으면 스트릭 중단
                
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
        
    except Exception as e:
        print(f"Error in _calculate_streak_days: {e}")
        return 0

async def _calculate_monthly_goal_percentage(db: AsyncSession, user_id: int):
    """사용자의 월간 목표 달성률을 계산합니다."""
    try:
        # 월간 목표는 예를 들어 월 100개 퀘스트 완료라고 가정
        monthly_target = 100
        
        # 이번 달 시작과 끝
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        # 이번 달 완료한 퀘스트 수 조회
        monthly_completed_result = await db.execute(
            select(func.count()).select_from(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True,
                models.Quest.finish_time >= start_of_month
            )
        )
        monthly_completed = monthly_completed_result.scalar_one() or 0
        
        # 달성률 계산 (최대 100%)
        return min(int((monthly_completed / monthly_target) * 100), 100)
        
    except Exception as e:
        print(f"Error in _calculate_monthly_goal_percentage: {e}")
        return 0

async def _calculate_level_progress(db: AsyncSession, user_id: int, current_level: int):
    """레벨업 진행률을 계산합니다."""
    try:
        # 다음 레벨에 필요한 경험치 계산 (예: 레벨^2 * 100)
        next_level_xp = (current_level + 1) ** 2 * 100
        
        # 현재 레벨 시작 경험치
        current_level_xp = current_level ** 2 * 100
        
        # 필요한 경험치
        xp_needed = next_level_xp - current_level_xp
        
        # 현재 경험치 (예: 완료된 퀘스트 수 * 10)
        completed_result = await db.execute(
            select(func.count()).select_from(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True
            )
        )
        completed_quests = completed_result.scalar_one() or 0
        current_xp = completed_quests * 10
        
        # 현재 레벨 내에서의 진행 경험치
        current_level_progress = current_xp - current_level_xp
        
        # 진행률 계산
        progress_percentage = min(int((current_level_progress / xp_needed) * 100), 99)
        
        return progress_percentage
        
    except Exception as e:
        print(f"Error in _calculate_level_progress: {e}")
        return 0

async def _get_calendar_data(db: AsyncSession, user_id: int):
    """한 달 간의 일별 활동 데이터를 생성합니다."""
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
    
    # 일별 완료된 퀘스트 수 조회
    result = await db.execute(
        select(
            func.date(models.Quest.finish_time).label('date'),
            func.count().label('count')
        ).filter(
            models.Quest.user_id == user_id,
            models.Quest.finish == True,
            models.Quest.finish_time >= start_of_month,
            models.Quest.finish_time <= end_of_month
        ).group_by(
            func.date(models.Quest.finish_time)
        )
    )
    
    # 결과를 날짜별 맵으로 변환
    daily_counts = {row.date.strftime('%Y-%m-%d'): row.count for row in result.all()}
    
    # 해당 월의 모든 날짜에 대한 데이터 생성
    calendar_data = []
    current_date = start_of_month
    while current_date <= end_of_month:
        date_str = current_date.strftime('%Y-%m-%d')
        count = daily_counts.get(date_str, 0)
        
        # 활동 레벨 결정 (0-3)
        activity_level = 0
        if count > 0:
            if count <= 2:
                activity_level = 1
            elif count <= 4:
                activity_level = 2
            else:
                activity_level = 3
        
        # 해당 날짜에 완료된 퀘스트 ID 가져오기
        if count > 0:
            quests_result = await db.execute(
                select(models.Quest.id).filter(
                    models.Quest.user_id == user_id,
                    models.Quest.finish == True,
                    func.date(models.Quest.finish_time) == current_date.date()
                )
            )
            quest_ids = [str(row[0]) for row in quests_result.all()]
        else:
            quest_ids = []
        
        calendar_data.append({
            "date": date_str,
            "activityLevel": activity_level,
            "completedQuestIds": quest_ids
        })
        
        current_date += timedelta(days=1)
    
    return calendar_data

async def _get_tag_statistics(db: AsyncSession, user_id: int):
    """사용자의 태그별 통계를 생성합니다."""
    # 현재는 샘플 데이터를 반환하고 있습니다.
    
    try:
        # 1. 사용자의 모든 퀘스트를 조회합니다.
        quest_result = await db.execute(
            select(models.Quest).filter(models.Quest.user_id == user_id)
        )
        quests = quest_result.scalars().all()
        
        # 2. 태그 정보를 집계합니다.
        tag_counts = {}
        for quest in quests:
            # 태그 정보가 JSON 문자열로 저장되어 있으므로 파싱합니다.
            try:
                if quest.tag:
                    tags = json.loads(quest.tag) if isinstance(quest.tag, str) else quest.tag
                    if isinstance(tags, list):
                        for tag in tags:
                            if tag in tag_counts:
                                tag_counts[tag] += 1
                            else:
                                tag_counts[tag] = 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        # 3. 총 태그 수를 계산합니다.
        total_count = sum(tag_counts.values()) if tag_counts else 1  # 0으로 나누기 방지
        
        # 4. 태그별 통계 데이터를 생성합니다.
        tags_data = [
            {
                "name": tag, 
                "count": count,
                "percentage": int((count / total_count) * 100)
            }
            for tag, count in tag_counts.items()
        ]
        
        # 5. 많이 사용된 순서로 정렬합니다.
        tags_data = sorted(tags_data, key=lambda x: x["count"], reverse=True)
        
        # 6. 데이터가 없는 경우 기본 태그 목록을 제공합니다.
        if not tags_data:
            tags_data = [
                {"name": "운동 및 스포츠", "count": 0, "percentage": 0},
                {"name": "공부", "count": 0, "percentage": 0},
                {"name": "자기개발", "count": 0, "percentage": 0},
                {"name": "취미", "count": 0, "percentage": 0},
                {"name": "명상 및 스트레칭", "count": 0, "percentage": 0},
                {"name": "기타", "count": 0, "percentage": 0},
            ]
        
        return tags_data
    
    except Exception as e:
        # 에러 로깅
        print(f"Error in _get_tag_statistics: {e}")
        # 기본 태그 목록 반환
        return [
            {"name": "운동 및 스포츠", "count": 0, "percentage": 0},
            {"name": "공부", "count": 0, "percentage": 0},
            {"name": "자기개발", "count": 0, "percentage": 0},
            {"name": "취미", "count": 0, "percentage": 0},
            {"name": "명상 및 스트레칭", "count": 0, "percentage": 0},
            {"name": "기타", "count": 0, "percentage": 0},
        ]

async def _get_weekly_activity(
    db: AsyncSession, 
    user_id: int, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """주간 활동 데이터를 생성합니다."""
    if not start_date:
        now = datetime.now()
        start_date = now - timedelta(days=6)  # 7일 동안의 데이터 (오늘 포함)
    
    if not end_date:
        end_date = datetime.now()
    
    # 일별 데이터 생성
    weekly_data = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # 해당 날짜에 완료된 퀘스트 수 계산
        completed_result = await db.execute(
            select(func.count()).select_from(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True,
                func.date(models.Quest.finish_time) == current_date.date()
            )
        )
        completed_quests = completed_result.scalar_one() or 0
        
        # 획득한 경험치 (예시)
        earned_xp = completed_quests * 350
        
        # 목표 달성 수 (예시)
        goal_achievement = min(completed_quests, 7)
        
        weekly_data.append({
            "date": date_str,
            "completedQuests": completed_quests,
            "earnedXp": earned_xp,
            "goalAchievement": goal_achievement
        })
        
        current_date += timedelta(days=1)
    
    return weekly_data

async def _get_monthly_activity(db: AsyncSession, user_id: int, start_date: datetime, end_date: datetime):
    """월간 활동 데이터를 생성합니다. 주 단위로 데이터를 집계합니다."""
    # 주 단위로 데이터 그룹화
    weeks_data = []
    
    # 시작일을 월요일로 조정
    days_since_monday = start_date.weekday()
    adjusted_start = start_date - timedelta(days=days_since_monday)
    
    # 4주 데이터 생성
    for week in range(4):
        week_start = adjusted_start + timedelta(weeks=week)
        week_end = week_start + timedelta(days=6)
        
        if week_end > end_date:
            week_end = end_date
        
        week_label = f"Week {week+1}"
        
        # 해당 주에 완료된 퀘스트 수 계산
        completed_result = await db.execute(
            select(func.count()).select_from(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True,
                func.date(models.Quest.finish_time) >= week_start.date(),
                func.date(models.Quest.finish_time) <= week_end.date()
            )
        )
        completed_quests = completed_result.scalar_one() or 0
        
        # 획득한 경험치 (예시)
        earned_xp = completed_quests * 300
        
        # 목표 달성 수 (예시)
        goal_achievement = min(completed_quests // 3, 7)
        
        weeks_data.append({
            "date": week_label,
            "completedQuests": completed_quests,
            "earnedXp": earned_xp,
            "goalAchievement": goal_achievement
        })
    
    return weeks_data

async def _get_yearly_activity(db: AsyncSession, user_id: int, start_date: datetime, end_date: datetime):
    """연간 활동 데이터를 생성합니다. 월 단위로 데이터를 집계합니다."""
    # 월 단위로 데이터 그룹화
    months_data = []
    
    # 12개월 데이터 생성
    for month in range(12):
        month_start = datetime(end_date.year, month + 1, 1)
        
        if month == 11:  # 12월일 경우
            month_end = datetime(end_date.year, 12, 31)
        else:
            month_end = datetime(end_date.year, month + 2, 1) - timedelta(days=1)
        
        # 시간 범위가 유효한지 확인
        if month_end < start_date or month_start > end_date:
            continue
        
        month_label = month_start.strftime('%b')  # 월 이름 (Jan, Feb, ...)
        
        # 해당 월에 완료된 퀘스트 수 계산
        completed_result = await db.execute(
            select(func.count()).select_from(models.Quest).filter(
                models.Quest.user_id == user_id,
                models.Quest.finish == True,
                func.date(models.Quest.finish_time) >= month_start.date(),
                func.date(models.Quest.finish_time) <= month_end.date()
            )
        )
        completed_quests = completed_result.scalar_one() or 0
        
        # 획득한 경험치 (예시)
        earned_xp = completed_quests * 250
        
        # 목표 달성 수 (예시)
        goal_achievement = min(completed_quests // 10, 7)
        
        months_data.append({
            "date": month_label,
            "completedQuests": completed_quests,
            "earnedXp": earned_xp,
            "goalAchievement": goal_achievement
        })
    
    return months_data