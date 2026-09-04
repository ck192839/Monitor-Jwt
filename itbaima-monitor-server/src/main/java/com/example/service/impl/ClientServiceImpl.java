package com.example.service.impl;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.entity.dto.Client;
import com.example.entity.dto.ClientDetail;
import com.example.entity.dto.ClientSsh;
import com.example.entity.vo.request.*;
import com.example.entity.vo.response.*;
import com.example.mapper.ClientDetailMapper;
import com.example.mapper.ClientMapper;
import com.example.mapper.ClientSshMapper;
import com.example.service.ClientService;
import com.example.utils.InfluxDbUtils;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class ClientServiceImpl  extends ServiceImpl<ClientMapper, Client> implements ClientService {
    private String registerToken = this.generateNewToken();

    private final Map<Integer, Client> clientIdCache = new ConcurrentHashMap<>();
    private final Map<String, Client> clientTokenCache = new ConcurrentHashMap<>();
    private final Map<Integer, ClientDetail> clientDetailCache = new ConcurrentHashMap<>();
    private final Set<Integer> clientDetailMissingCache = ConcurrentHashMap.newKeySet();
    @Resource
    private ClientDetailMapper detailMapper;

    @Resource
    InfluxDbUtils influx;

    @Resource
    ClientSshMapper sshMapper;

    @PostConstruct
    public void initClientCache() {  // 初始化客户端缓存，从数据库中加载所有客户端到缓存中
        clientTokenCache.clear();
        clientIdCache.clear();
        this.list().forEach(this::addClientCache);
    }
    @Override
    public String registerToken() {
        return registerToken;
    }
    @Override
    public Client findClientById(int id) {
        return clientIdCache.get(id);
    }

    @Override
    public Client findClientByToken(String token) {
        return clientTokenCache.get(token);
    }


    @Override
    public boolean verifyAndRegister(String token) {
        if (this.registerToken.equals(token)) {
            int id = this.randomClientId();
            Client client = new Client(id, "未命名主机", token, "cn", "未命名节点", new Date());
            if (this.save(client)) {
                registerToken = this.generateNewToken();
                this.addClientCache(client);
                return true;
            }
        }
        System.out.println("注册Token错误");
        return false;
    }

    @Override
    public void updateClientDetail(ClientDetailVO vo, Client client) {
        ClientDetail detail=new ClientDetail();
        BeanUtils.copyProperties(vo,detail);
        detail.setId(client.getId());
        if(Objects.nonNull(detailMapper.selectById(client.getId()))){
            detailMapper.updateById(detail);
        }
        else{
            detailMapper.insert(detail);
        }
        clientDetailMissingCache.remove(client.getId());
        clientDetailCache.put(client.getId(), detail);
    }

    private final Map<Integer, RuntimeDetailVO> currentRuntime = new ConcurrentHashMap<>();

    @Override
    public void updateRuntimeDetail(RuntimeDetailVO vo, Client client) {
        currentRuntime.put(client.getId(), vo);
        influx.writeRuntimeData(client.getId(), vo);
    }
    @Override
    public List<ClientPreviewVO> listClients() {
        List<Client> clients = new ArrayList<>(clientIdCache.values());
        Map<Integer, ClientDetail> details = loadClientDetails(clients);
        return clients.stream().map(client -> {
            return buildClientPreview(client, details.get(client.getId()), currentRuntime.get(client.getId()));
        }).toList();
    }
    @Override
    public List<ClientSimpleVO> listSimpleList() {
        List<Client> clients = new ArrayList<>(clientIdCache.values());
        Map<Integer, ClientDetail> details = loadClientDetails(clients);
        return clients.stream().map(client -> {
            ClientSimpleVO vo = client.asViewObject(ClientSimpleVO.class);
            ClientDetail detail = details.get(vo.getId());
            if (detail != null) {
                BeanUtils.copyProperties(detail, vo);
            } else {
                vo.setOsName("未知");
                vo.setOsVersion("");
                vo.setIp("未知");
            }
            return vo;
        }).toList();
    }

    private Map<Integer, ClientDetail> loadClientDetails(Collection<Client> clients) {
        if (clients.isEmpty()) {
            return Collections.emptyMap();
        }
        List<Integer> ids = clients.stream().map(Client::getId).toList();
        List<Integer> missingIds = ids.stream()
                .filter(id -> !clientDetailCache.containsKey(id) && !clientDetailMissingCache.contains(id))
                .toList();
        if (!missingIds.isEmpty()) {
            List<ClientDetail> details = detailMapper.selectBatchIds(missingIds);
            if (details != null) {
                Set<Integer> foundIds = details.stream()
                        .filter(detail -> detail.getId() != null)
                        .map(ClientDetail::getId)
                        .collect(java.util.stream.Collectors.toSet());
                details.stream()
                        .filter(detail -> detail.getId() != null)
                        .forEach(detail -> clientDetailCache.put(detail.getId(), detail));
                missingIds.stream()
                        .filter(id -> !foundIds.contains(id))
                        .forEach(clientDetailMissingCache::add);
            }
        }
        return ids.stream()
                .filter(clientDetailCache::containsKey)
                .collect(java.util.stream.Collectors.toMap(id -> id, clientDetailCache::get));
    }

    private ClientPreviewVO buildClientPreview(Client client, ClientDetail detail, RuntimeDetailVO runtime) {
        ClientPreviewVO vo = new ClientPreviewVO();
        vo.setId(client.getId());
        vo.setName(client.getName());
        vo.setLocation(client.getLocation());
        if (detail == null) {
            applyMissingDetailDefaults(vo);
        } else {
            vo.setOsName(detail.getOsName());
            vo.setOsVersion(detail.getOsVersion());
            vo.setIp(detail.getIp());
            vo.setCpuName(detail.getCpuName());
            vo.setCpuCore(detail.getCpuCore());
            vo.setMemory(detail.getMemory());
        }
        if (this.isOnline(runtime)) {
            vo.setCpuUsage(runtime.getCpuUsage());
            vo.setMemoryUsage(runtime.getMemoryUsage());
            vo.setNetworkUpload(runtime.getNetworkUpload());
            vo.setNetworkDownload(runtime.getNetworkDownload());
            vo.setOnline(true);
        }
        return vo;
    }



    @Override
    public void renameClient(RenameClientVO vo) {
        this.update(Wrappers.<Client>update().eq("id", vo.getId()).set("name", vo.getName()));
        this.initClientCache();
    }

    @Override
    public void renameNode(RenameNodeVO vo) {
        this.update(Wrappers.<Client>update().eq("id", vo.getId())
                .set("node", vo.getNode())
                .set("location", vo.getLocation()));
        this.initClientCache();
    }

    @Override
    public void deleteClient(int clientId) {//influxdb数据不管
        this.removeById(clientId);
        detailMapper.deleteById(clientId);
        clientDetailCache.remove(clientId);
        clientDetailMissingCache.remove(clientId);
        this.initClientCache();
        currentRuntime.remove(clientId);
    }

    @Override
    public void saveClientSshConnection(SshConnectionVO vo) {
        Client client = clientIdCache.get(vo.getId());
        if(client == null) return;
        ClientSsh ssh = new ClientSsh();
        BeanUtils.copyProperties(vo, ssh);
        if(Objects.nonNull(sshMapper.selectById(client.getId()))) {
            sshMapper.updateById(ssh);
        } else {
            sshMapper.insert(ssh);
        }
    }

    @Override
    public SshSettingsVO sshSettings(int clientId) {
        ClientDetail detail = detailMapper.selectById(clientId);
        ClientSsh ssh = sshMapper.selectById(clientId);
        SshSettingsVO vo;
        if(ssh == null) {
            vo = new SshSettingsVO();
        } else {
            vo = ssh.asViewObject(SshSettingsVO.class);
        }
        vo.setIp(detail == null || detail.getIp() == null ? "未知" : detail.getIp());
        return vo;
    }


    private boolean isOnline(RuntimeDetailVO runtime) {
        return runtime != null && System.currentTimeMillis() - runtime.getTimestamp() < 60 * 1000;
    }
    @Override
    public ClientDetailsVO clientDetails(int clientId) {
        ClientDetailsVO vo = this.clientIdCache.get(clientId).asViewObject(ClientDetailsVO.class);
        ClientDetail detail = detailMapper.selectById(clientId);
        if (detail != null) {
            BeanUtils.copyProperties(detail, vo);
        } else {
            applyMissingDetailDefaults(vo);
        }
        vo.setOnline(this.isOnline(currentRuntime.get(clientId)));
        return vo;
    }

    @Override
    public RuntimeDetailVO clientRuntimeDetailsNow(int clientId){
        return currentRuntime.get(clientId);
    }

    @Override
    public RuntimeHistoryVO clientRuntimeDetailsHistory(int clientId) {
        RuntimeHistoryVO vo= influx.readRuntimeData(clientId);
        ClientDetail detail=detailMapper.selectById(clientId);
        if (detail != null) {
            BeanUtils.copyProperties(detail,vo);
        }
        return vo;
    }


    private void addClientCache(Client client) {
        clientIdCache.put(client.getId(), client);
        clientTokenCache.put(client.getToken(), client);
    }

    private void applyMissingDetailDefaults(ClientPreviewVO vo) {
        vo.setOsName("未知");
        vo.setOsVersion("");
        vo.setIp("未知");
        vo.setCpuName("未知");
        vo.setCpuCore(0);
        vo.setMemory(0);
    }

    private void applyMissingDetailDefaults(ClientDetailsVO vo) {
        vo.setOsName("未知");
        vo.setOsVersion("");
        vo.setIp("未知");
        vo.setCpuName("未知");
        vo.setCpuCore(0);
        vo.setMemory(0);
    }

    private int randomClientId() {
        return new Random().nextInt(90000000) + 10000000;
    }
    private String generateNewToken() {
        String CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        SecureRandom random = new SecureRandom();
        StringBuilder sb = new StringBuilder(24);
        for (int i = 0; i < 24; i++)
            sb.append(CHARACTERS.charAt(random.nextInt(CHARACTERS.length())));
        System.out.println("生成的Token: " + sb.toString());
        return sb.toString();
    }

}
