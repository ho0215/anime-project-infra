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

# State address migration: VPC endpoint SG moved out of endpoints → security module
# (all other SGs live there). Prevents destroy/recreate of the live SG that the
# SSM interface endpoints still reference.
moved {
  from = module.endpoints.aws_security_group.vpce
  to   = module.security.aws_security_group.vpce
}
