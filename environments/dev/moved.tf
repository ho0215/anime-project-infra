# State address migration: ALB resources moved out of compute → alb module.
# Prevents destroy/recreate of the live load balancer / target group / listener.
moved {
  from = module.compute.aws_lb.main
  to   = module.alb.aws_lb.main
}

moved {
  from = module.compute.aws_lb_target_group.app
  to   = module.alb.aws_lb_target_group.app
}

moved {
  from = module.compute.aws_lb_listener.http
  to   = module.alb.aws_lb_listener.http
}
