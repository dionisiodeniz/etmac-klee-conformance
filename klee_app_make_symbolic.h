#ifdef KLEE_EXECUTION
klee_make_symbolic(&ghost_scheduling_policy, sizeof(int),"policy");
klee_make_symbolic(&ghost_sched_param_thread, sizeof(pthread_t),"ghost_sched_param_thread");
klee_make_symbolic(&t1,sizeof(pthread_t),"t1");
klee_make_symbolic(&ghost_t1_sched_parameter.sched_priority, sizeof(ghost_t1_sched_parameter.sched_priority),"ghost_t1_sched_parameter.sched_priority");
klee_make_symbolic(&ghost_t1_scheduling_policy,sizeof(ghost_t1_scheduling_policy),"ghost_t1_scheduling_policy");
klee_make_symbolic(&t2,sizeof(pthread_t),"t2");
klee_make_symbolic(&ghost_t2_sched_parameter.sched_priority, sizeof(ghost_t2_sched_parameter.sched_priority),"ghost_t2_sched_parameter.sched_priority");
klee_make_symbolic(&ghost_t2_scheduling_policy,sizeof(ghost_t2_scheduling_policy),"ghost_t2_scheduling_policy");
#endif
