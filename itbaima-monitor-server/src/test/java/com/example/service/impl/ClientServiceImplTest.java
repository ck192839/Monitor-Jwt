package com.example.service.impl;

import com.example.entity.dto.Client;
import com.example.mapper.ClientDetailMapper;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Date;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

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
}
