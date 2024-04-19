#include <unistd.h>
#include <sched.h>
#include <stdio.h>
#include <pthread.h>

pthread_t t1;
pthread_t t2;

void *thread_main1(void *parg){
  int cnt = 10;
  struct sched_param p;

  p.sched_priority = 2;
  pthread_setschedparam_proxy(pthread_self_proxy(), SCHED_FIFO, &p);

  while (cnt--){
    printf("thread1\n");
    sleep(1);
  }
  
  return NULL;
}

void *thread_main2(void *parg){
  int cnt = 10;
  struct sched_param p;

  p.sched_priority = 3;
  pthread_setschedparam_proxy(pthread_self_proxy(), SCHED_FIFO, &p);

  while (cnt--){
    printf("thread2\n");
    sleep(1);
  }
  
  return NULL;
}

int main(){
  void *ret;
  struct sched_param p;

  if (pthread_create_proxy(&t1, NULL,thread_main1,NULL) <0){
    printf("Error creating thread1\n");
  }
  if (pthread_create_proxy(&t2, NULL,thread_main2,NULL) <0){
    printf("Error creating thread2\n");
  };

  printf("t1=%d, t2=%d\n",t1,t2);
  // moving the priority setting to the thread main functions
  // p.sched_priority = 2;
  // pthread_setschedparam_proxy(t1, SCHED_FIFO, &p);
  // p.sched_priority = 3;
  // pthread_setschedparam_proxy(t2, SCHED_FIFO, &p);
  
  pthread_join_proxy(t1,&ret);
  pthread_join_proxy(t2,&ret);
}
