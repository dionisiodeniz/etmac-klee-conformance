ghost_scheduling_policy = policy;
ghost_sched_param_thread = t;
if (t == t1){
	ghost_t1_sched_parameter.sched_priority = p->sched_priority;
	ghost_t1_scheduling_policy = policy;
}
if (t == t2){
	ghost_t2_sched_parameter.sched_priority = p->sched_priority;
	ghost_t2_scheduling_policy = policy;
}
