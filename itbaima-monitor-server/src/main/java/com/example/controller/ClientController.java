package com.example.controller;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.entity.RestBean;
import com.example.entity.dto.Account;
import com.example.entity.dto.Client;
import com.example.entity.vo.request.ClientDetailVO;
import com.example.entity.vo.request.RenameNodeVO;
import com.example.entity.vo.request.RuntimeDetailVO;
import com.example.entity.vo.response.RuntimeHistoryVO;
import com.example.mapper.ClientMapper;
import com.example.service.AccountService;
import com.example.service.ClientService;
import com.example.utils.Const;
import jakarta.annotation.Resource;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
    @RequestMapping("/monitor")
    public class ClientController {

    @Resource
    ClientService service;

    @Resource
    AccountService accountService;


    @GetMapping("/register")
    public RestBean<Void> registerClient(@RequestHeader("Authorization") String token) {
        return service.verifyAndRegister(token) ?
                RestBean.success() : RestBean.failure(401, "客户端注册失败，请检查Token是否正确");
    }

    @PostMapping("/detail")
    public RestBean<Void> sendDetail(@RequestAttribute(Const.ATTR_CLIENT) Client client,
                                     @RequestBody @Valid ClientDetailVO vo) {
        service.updateClientDetail(vo, client);
        return RestBean.success();
    }

    @PostMapping("/node")
    public RestBean<Void> renameNode(@RequestBody @Valid RenameNodeVO vo,
                                     @RequestAttribute(Const.ATTR_USER_ID) int userId,
                                     @RequestAttribute(Const.ATTR_USER_ROLE) String userRole) {
        service.renameNode(vo);
        return RestBean.success();

    }

    @PostMapping("/runtime")
    public RestBean<Void> updateRuntimeDetails(@RequestAttribute(Const.ATTR_CLIENT) Client client,
                                               @RequestBody @Valid RuntimeDetailVO vo) {
        service.updateRuntimeDetail(vo, client);
        return RestBean.success();
    }


}


