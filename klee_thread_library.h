#ifdef KLEE_EXECUTION

#define pthread_create pthread_create_klee
#define pthread_setschedparam pthread_setschedparam_klee
#define pthread_join pthread_join_klee
#define pthread_self pthread_self_klee

// Fake calls
int klee_current_self = -1;

pthread_t pthread_self_klee(){
  return klee_current_self;
}

int pthread_create_klee(pthread_t* t, pthread_attr_t *attr, void *(*start_func)(void *), void *arg){
  static int next =0;
  *t = next++;

  // Serialize the execution to evaluate the parameter setup
  klee_current_self = *t;
  start_func(arg);

  return 0;
}

int pthread_setschedparam_klee(pthread_t t, int policy, struct sched_param *p){
#include "klee_app_thread_setschedparam_assertions.h"
  return 0;
}
int pthread_join_klee(pthread_t t, void **retval){
  return 0;
}
#else

#define pthread_create_proxy pthread_create
#define pthread_setschedparam_proxy pthread_setschedparam
#define pthread_join_proxy pthread_join

#endif