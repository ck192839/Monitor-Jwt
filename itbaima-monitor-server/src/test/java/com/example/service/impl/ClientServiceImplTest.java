package com.example.service.impl;

import com.example.entity.dto.Client;
import com.example.entity.dto.ClientDetail;
import com.example.entity.vo.response.RuntimeHistoryVO;
import com.example.mapper.ClientDetailMapper;
import com.example.utils.InfluxDbUtils;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Date;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.ArgumentMatchers.anyList;

class ClientServiceImplTest {

    @Test
    void listClientsShouldIncludeClientWithoutUploadedDetail() {
        ClientServiceImpl service = new ClientServiceImpl();
        ClientDetailMapper detailMapper = mock(ClientDetailMapper.class);
        ReflectionTestUtils.setField(service, "detailMapper", detailMapper);
        ReflectionTestUtils.invokeMethod(service, "addClientCache",
                new Client(1, "未命名主机", "token", "cn", "未命名节点", new Date()));
        when(detailMapper.selectById(1)).thenReturn(null);

        var result = service.listClients();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("未命名主机");
        assertThat(result.get(0).getOsName()).isEqualTo("未知");
    }

    @Test
    void historyShouldReturnWithoutDetailRecord() {
        ClientServiceImpl service = new ClientServiceImpl();
        ClientDetailMapper detailMapper = mock(ClientDetailMapper.class);
        InfluxDbUtils influx = mock(InfluxDbUtils.class);
        ReflectionTestUtils.setField(service, "detailMapper", detailMapper);
        ReflectionTestUtils.setField(service, "influx", influx);
        when(detailMapper.selectById(1)).thenReturn(null);
        when(influx.readRuntimeData(1)).thenReturn(new RuntimeHistoryVO());

        var result = service.clientRuntimeDetailsHistory(1);

        assertThat(result).isNotNull();
        assertThat(result.getList()).isEmpty();
    }

    @Test
    void listClientsShouldLoadDetailsInOneBatchQuery() {
        ClientServiceImpl service = new ClientServiceImpl();
        ClientDetailMapper detailMapper = mock(ClientDetailMapper.class);
        ReflectionTestUtils.setField(service, "detailMapper", detailMapper);
        ReflectionTestUtils.invokeMethod(service, "addClientCache",
                new Client(1, "主机1", "token-1", "cn", "节点1", new Date()));
        ReflectionTestUtils.invokeMethod(service, "addClientCache",
                new Client(2, "主机2", "token-2", "cn", "节点2", new Date()));
        ClientDetail detail = new ClientDetail();
        detail.setId(1);
        detail.setOsName("Linux");
        when(detailMapper.selectBatchIds(anyList()))
                .thenReturn(java.util.List.of(detail));

        var result = service.listClients();

        verify(detailMapper).selectBatchIds(org.mockito.ArgumentMatchers.argThat(ids ->
                ids.size() == 2 && ids.containsAll(java.util.List.of(1, 2))));
        verify(detailMapper, never()).selectById(1);
        verify(detailMapper, never()).selectById(2);
        assertThat(result).anyMatch(item -> item.getId() == 1 && "Linux".equals(item.getOsName()));
    }
}
