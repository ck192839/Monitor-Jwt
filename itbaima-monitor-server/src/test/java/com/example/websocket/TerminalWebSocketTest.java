package com.example.websocket;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

class TerminalWebSocketTest {

    private ThreadPoolExecutor executor;

    @BeforeEach
    void setUp() {
        Object service = ReflectionTestUtils.getField(new TerminalWebSocket(), "service");
        assertThat(service).isInstanceOf(ThreadPoolExecutor.class);
        executor = (ThreadPoolExecutor) service;
    }

    @AfterEach
    void tearDown() {
        executor.shutdownNow();
    }

    @Test
    void shouldCreateEquivalentSingleThreadExecutor() {
        assertThat(executor.getCorePoolSize()).isEqualTo(1);
        assertThat(executor.getMaximumPoolSize()).isEqualTo(1);
        assertThat(executor.getKeepAliveTime(TimeUnit.MILLISECONDS)).isZero();
        assertThat(executor.getQueue()).isInstanceOf(LinkedBlockingQueue.class);
        assertThat(executor.getQueue().remainingCapacity()).isEqualTo(Integer.MAX_VALUE);
        assertThat(executor.allowsCoreThreadTimeOut()).isFalse();
        assertThat(executor.getRejectedExecutionHandler())
                .isInstanceOf(ThreadPoolExecutor.AbortPolicy.class);
    }

    @Test
    void shouldExecuteSubmittedTasksSequentially() throws Exception {
        CountDownLatch firstTaskStarted = new CountDownLatch(1);
        CountDownLatch releaseFirstTask = new CountDownLatch(1);
        List<Integer> executionOrder = Collections.synchronizedList(new ArrayList<>());

        Future<?> firstTask = executor.submit(() -> {
            firstTaskStarted.countDown();
            try {
                releaseFirstTask.await();
                executionOrder.add(1);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        assertThat(firstTaskStarted.await(1, TimeUnit.SECONDS)).isTrue();
        Future<?> secondTask = executor.submit(() -> executionOrder.add(2));
        assertThat(secondTask.isDone()).isFalse();

        releaseFirstTask.countDown();
        firstTask.get(1, TimeUnit.SECONDS);
        secondTask.get(1, TimeUnit.SECONDS);

        assertThat(executionOrder).containsExactly(1, 2);
    }
}
