# 1. 알림을 보낼 SNS 토픽(채널) 생성
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-topic"
}

# 2. 이메일 구독 설정 (이메일 수신자 등록)
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# 3. EC2 CPU 사용률 경보 (ASG 기준)
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-cpu-high-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120" # 120초(2분) 동안 검사
  statistic           = "Average"
  threshold           = "80"  # 평균 CPU 80% 이상일 때 경보!

  alarm_description   = "ASG 내 EC2 인스턴스들의 평균 CPU 사용률이 80%를 초과했습니다."
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn] # 상태가 정상으로 복구되었을 때도 알림

  dimensions = {
    AutoScalingGroupName = var.asg_name
  }
}

# 4. ALB 5XX 서버 에러 경보
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.project_name}-alb-5xx-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60" # 60초(1분) 동안 검사
  statistic           = "Sum"
  threshold           = "10" # 1분 동안 5XX 에러가 10번 이상 발생하면 경보!

  alarm_description   = "ALB에서 5XX 서버 에러가 비정상적으로 많이 발생하고 있습니다."
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }
}