"""
Script gerador de bases de dados técnicas com 200 tópicos REAIS e ÚNICOS (sem repetições ou clones sintéticos).
- Cenário A: 100 FAQs de suporte corporativo Microsoft (IDs 1 a 100)
- Cenário B: 100 Diálogos/Logs de suporte técnico Ubuntu (IDs 101 a 200)
- 60 Consultas analíticas de teste do Padrão-Ouro (Ground Truth) com relevância binária
"""

import json
import os

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# =====================================================================
# CENÁRIO A: 100 DOCUMENTOS MICROSOFT AUTÊNTICOS E DISTINTOS (IDs 1-100)
# =====================================================================
ms_docs_raw = [
    (1, "Como resolver falhas de conectividade e IP inválido no Windows", "Conectividade",
     "Sintoma: O computador exibe status 'Sem Internet' ou endereço IP de autoconfiguração 169.254.x.x. "
     "Causa: Falha na concessão de concessão DHCP pelo roteador ou corrupção do cache DNS e pilha TCP/IP. "
     "Solução técnica: Abra o Prompt de Comando (CMD) como Administrador e execute: "
     "1. ipconfig /release para liberar a concessão atual. "
     "2. ipconfig /renew para solicitar novo endereço IP ao servidor DHCP. "
     "3. ipconfig /flushdns para limpar o cache de resolução de nomes. "
     "4. netsh int ip reset e netsh winsock reset para restaurar o catálogo de sockets de rede. Reinicie a estação."),

    (2, "Configuração e diagnóstico de conexão VPN corporativa no Windows 11", "Conectividade",
     "Sintoma: Falha ao estabelecer túnel VPN corporativo com erro 800 ou 809. "
     "Causa: Bloqueio de portas UDP 500/4500 por firewall local ou NAT traversal desabilitado. "
     "Solução técnica: Verifique as configurações de rede em Configurações > Rede e Internet > VPN. "
     "Adicione a chave AssumeUDPEncapsulationContextOnSendRule no registro em HKLM\\SYSTEM\\CurrentControlSet\\Services\\PolicyAgent com valor DWORD 2. "
     "Garanta que o serviço 'IKE and AuthIP IPsec Keying Modules' esteja em execução."),

    (3, "Resolução de lentidão em downloads e latência alta no adaptador Wi-Fi", "Conectividade",
     "Sintoma: Navegação web lenta com frequentes quedas de pacotes na rede sem fio corporativa. "
     "Causa: Interferência de canal na frequência de 2.4 GHz ou driver desatualizado da placa de rede Wi-Fi. "
     "Solução: Atualize o driver da placa no Gerenciador de Dispositivos. Altere a largura de canal nas propriedades "
     "avançadas do adaptador para 20MHz ou mude a conexão preferencial para a banda de 5 GHz."),

    (4, "Computador não acessa pastas compartilhadas na rede interna (Erro 0x80070035)", "Conectividade",
     "Sintoma: Ao tentar acessar \\\\servidor\\compartilhamento o Windows retorna erro 'O caminho da rede não foi encontrado'. "
     "Causa: Protocolo SMBv1 desabilitado ou descoberta de rede desativada no perfil de rede pública. "
     "Solução: Altere o perfil de rede de Público para Privado. No Painel de Controle > Recursos do Windows, "
     "certifique-se de que o suporte a compartilhamento de arquivos SMB 2.0/3.0 está habilitado."),

    (5, "Falha de resolução de nomes internos via servidor DNS secundário", "Conectividade",
     "Sintoma: Máquinas clientes conseguem pingar endereços IP externos, mas não resolvem domínios corporativos locais. "
     "Causa: Ordem incorreta de servidores DNS configurada no adaptador de rede local. "
     "Solução: Configure estaticamente o DNS primário apontando para o Domain Controller corporativo e execute ipconfig /flushdns."),

    (6, "Bloqueio de conexões de entrada na Área de Trabalho Remota (RDP porta 3389)", "Conectividade",
     "Sintoma: Não é possível conectar via RDP no host remoto, recebendo mensagem de timeout. "
     "Causa: Regra de entrada do Windows Defender Firewall para Área de Trabalho Remota desativada. "
     "Solução: No Firewall do Windows com Segurança Avançada, ative a regra pré-definida 'Área de Trabalho Remota - Modo de Usuário (TCP-In)'. "
     "Verifique se o serviço TermService está ativo."),

    (7, "Conflito de endereço IP estático na sub-rede corporativa", "Conectividade",
     "Sintoma: Notificação do Windows informando 'Existe um conflito de endereço IP com outro sistema na rede'. "
     "Causa: Dois dispositivos configurados manualmente com o mesmo endereço IPv4 estático. "
     "Solução: Utilize o comando arp -a para identificar o endereço MAC conflitante e reconfigure a máquina afetada para obter IP dinamicamente via DHCP."),

    (8, "Problemas de comunicação após alteração da MTU no adaptador de rede", "Conectividade",
     "Sintoma: Alguns sites carregam normalmente, mas sistemas internos corporativos e uploads travam. "
     "Causa: Valor de MTU (Maximum Transmission Unit) muito alto provocando fragmentação excessiva de pacotes. "
     "Solução: Execute netsh interface ipv4 show subinterfaces para consultar e netsh interface ipv4 set subinterface 'Ethernet' mtu=1492 store=persistent."),

    (9, "Diagnóstico de perda de pacotes e jitter em chamadas Microsoft Teams", "Conectividade",
     "Sintoma: Áudio robótico e vídeo congelando em reuniões do Teams. "
     "Causa: Concorrência de banda e ausência de priorização QoS para as portas UDP 3478-3481. "
     "Solução: Configure políticas de QoS de grupo (GPO) no Active Directory reservando DSCP 46 para pacotes de áudio do Teams."),

    (10, "Adaptador de rede Ethernet desconecta intermitentemente ao entrar em repouso", "Conectividade",
     "Sintoma: A rede cai após alguns minutos de inatividade do usuário. "
     "Causa: Gerenciamento de energia do Windows desligando o adaptador para economizar energia. "
     "Solução: No Gerenciador de Dispositivos > Placa de Rede > Propriedades > Gerenciamento de Energia, desmarque 'O computador pode desligar este dispositivo para economizar energia'."),

    (11, "Procedimento para redefinição de senha e desbloqueio de conta no Active Directory", "Autenticação",
     "Sintoma: Usuário não consegue fazer login na estação de trabalho com a mensagem 'Sua conta foi bloqueada'. "
     "Causa: Excesso de tentativas incorretas de senha que atingiram o limite da política de bloqueio do domínio. "
     "Solução técnica: O administrador deve abrir o console 'Usuários e Computadores do Active Directory' (dsa.msc), "
     "localizar a conta do colaborador, acessar Propriedades > Conta, marcar a opção 'Desbloquear conta' e selecionar 'Redefinir Senha' "
     "marcando 'O usuário deve alterar a senha no próximo logon'."),

    (12, "Erro de relação de confiança entre a estação de trabalho e o domínio primário", "Autenticação",
     "Sintoma: Ao autenticar o Windows exibe 'A relação de confiança entre esta estação de trabalho e o domínio primário falhou'. "
     "Causa: Senha da conta de máquina no Active Directory dessincronizada com o computador cliente. "
     "Solução técnica: Faça login com uma conta de administrador local. Abra o PowerShell como Administrador e execute: "
     "Test-ComputerSecureChannel -Repair -Credential (Get-Credential). Insira credenciais de admin de domínio para restabelecer a confiança."),

    (13, "Configuração e solução de problemas com autenticação multifator (MFA) no Entra ID", "Autenticação",
     "Sintoma: O aplicativo Microsoft Authenticator não recebe notificações push de aprovação. "
     "Causa: Notificações do celular desativadas ou dessincronização do relógio do dispositivo com os servidores NTP. "
     "Solução: Acesse https://mysignins.microsoft.com/security-info, exclua o método antigo e reconfigure o aplicativo Authenticator escaneando o QR code."),

    (14, "Falha de autenticação Kerberos por desvio de horário (Clock Skew)", "Autenticação",
     "Sintoma: Usuários não conseguem autenticar em recursos de rede internos da empresa. "
     "Causa: Diferença de horário entre o relógio da estação cliente e o Domain Controller superior a 5 minutos. "
     "Solução: Ressincronize o relógio da máquina executando no CMD como Administrador: w32tm /resync /force."),

    (15, "Credenciais do Outlook solicitadas repetidamente mesmo com a senha correta", "Autenticação",
     "Sintoma: Janela pop-up do Outlook solicitando login a cada poucos minutos. "
     "Causa: Credenciais corrompidas salvas no Gerenciador de Credenciais do Windows. "
     "Solução: Feche o Outlook. Acesse o Painel de Controle > Gerenciador de Credenciais > Credenciais do Windows. "
     "Remova todas as entradas associadas ao MicrosoftOffice e conta corporativa. Reinicie o Outlook e informe a senha novamente."),

    (16, "Políticas de Grupo (GPO) não são aplicadas após alteração de permissões", "Autenticação",
     "Sintoma: Computador não recebe novas diretivas de segurança corporativas. "
     "Causa: Cache local de GPO desatualizado ou falha de leitura da pasta SYSVOL. "
     "Solução: Execute o comando gpupdate /force no terminal e verifique se há erros através do comando gpresult /h relatorio_gpo.html."),

    (17, "PIN do Windows Hello parou de funcionar após troca de placa-mãe", "Autenticação",
     "Sintoma: Mensagem 'Ocorreu um problema e seu PIN não está disponível' na tela de bloqueio. "
     "Causa: O chip TPM (Trusted Platform Module) foi reiniciado ou trocado, invalidando as chaves criptográficas locais. "
     "Solução: Efetue login com a senha convencional da conta, acesse Configurações > Contas > Opções de Entrada e clique em 'Remover PIN' e configure um novo."),

    (18, "Como habilitar autenticação baseada em certificados digitais (Smart Card)", "Autenticação",
     "Sintoma: O leitor de cartão inteligente não é reconhecido no momento do logon no Windows. "
     "Causa: Serviço de Cartão Inteligente (SCardSvr) parado ou driver minidriver do fabricante ausente. "
     "Solução: Inicie o serviço 'Smart Card' em services.msc e instale o driver oficial do leitor criptográfico."),

    (19, "Desativação de contas inativas e auditoria de logons mal-sucedidos no Windows Server", "Autenticação",
     "Sintoma: Falhas repetidas de auditoria com Event ID 4625 no Visualizador de Eventos. "
     "Causa: Tentativas sucessivas de força bruta contra contas desativadas ou de serviço. "
     "Solução: Configure regras de bloqueio de conta via GPO e utilize o script Search-ADAccount -AccountInactive para desabilitar usuários obsoletos."),

    (20, "Problemas de sincronização de senhas híbridas entre Active Directory local e Microsoft 365", "Autenticação",
     "Sintoma: Usuário altera a senha local mas o portal web da nuvem continua exigindo a senha anterior. "
     "Causa: Agente Microsoft Entra Connect (antigo Azure AD Connect) com sincronização de hash de senha travada. "
     "Solução: Abra o PowerShell no servidor de sincronização e execute Start-ADSyncSyncCycle -PolicyType Delta."),

    (21, "Recuperação de travamento de sistema operacional e tela azul (BSOD CRITICAL_PROCESS_DIED)", "Sistema Operacional",
     "Sintoma: O computador reinicia subitamente apresentando tela azul com código de parada CRITICAL_PROCESS_DIED. "
     "Causa: Arquivos críticos do sistema corrompidos ou falha em drivers de dispositivos de baixo nível. "
     "Solução técnica: Inicialize o sistema em Modo de Segurança com Prompt de Comando e execute: "
     "1. sfc /scannow para verificar e reparar a integridade de arquivos do Windows. "
     "2. DISM /Online /Cleanup-Image /RestoreHealth para reparar a imagem do sistema usando o Windows Update como fonte. "
     "3. Verifique os arquivos de despejo minidump em C:\\Windows\\Minidump usando a ferramenta BlueScreenView."),

    (22, "Alto uso de disco em 100% no Gerenciador de Tarefas do Windows 10/11", "Sistema Operacional",
     "Sintoma: Computador fica excessivamente lento, congelando janelas com disco rígido operando constantemente em 100%. "
     "Causa: Conflito no serviço SysMain (antigo SuperFetch) ou serviço de Pesquisa do Windows (Windows Search). "
     "Solução: Abra o services.msc, localize o serviço 'SysMain', altere o Tipo de Inicialização para 'Desativado' e clique em 'Parar'. "
     "Execute chkdsk C: /f /r para verificar integridade física de setores do disco."),

    (23, "Windows Update travado em 'Baixando atualizações 0%' ou apresentando erro 0x80070002", "Sistema Operacional",
     "Sintoma: O sistema não conclui a instalação de patches cumulativos de segurança. "
     "Causa: Arquivos temporários do catálogo de distribuição de software corrompidos. "
     "Solução técnica: Abra o CMD como Admin e pare os serviços com net stop wuauserv e net stop bits. "
     "Renomeie a pasta C:\\Windows\\SoftwareDistribution para SoftwareDistribution.old. Reinicie os serviços com net start wuauserv."),

    (24, "Computador travado em loop de reparo automático na inicialização", "Sistema Operacional",
     "Sintoma: A máquina liga e entra direto na tela azul 'Reparo Automático não pôde reparar seu computador'. "
     "Causa: Registro de inicialização BCD (Boot Configuration Data) corrompido. "
     "Solução: Acesse Opções Avançadas > Prompt de Comando e execute: bootrec /fixmbr, bootrec /fixboot, bootrec /rebuildbcd."),

    (25, "Como restaurar o Windows para um ponto de restauração anterior", "Sistema Operacional",
     "Sintoma: O sistema apresentou instabilidade após a instalação de um software ou driver incompatível. "
     "Causa: Alterações estruturais no registro e drivers do sistema. "
     "Solução: Pressione Win + R, digite rstrui.exe e selecione um ponto de restauração anterior à data do problema ocorrido."),

    (26, "Memória RAM com alto consumo pelo processo 'Interrupções do Sistema'", "Sistema Operacional",
     "Sintoma: O processo System Interrupts consome mais de 30% da CPU permanentemente. "
     "Causa: Conflito de hardware ou driver com defeito enviando sinais de interrupção em loop. "
     "Solução: Atualize a BIOS/UEFI e os drivers do chipset da placa-mãe. Desconecte periféricos USB secundários."),

    (27, "Erro 'O Windows não pôde iniciar porque o arquivo winload.efi está ausente ou corrompido'", "Sistema Operacional",
     "Sintoma: Erro 0xc000000e na tela de boot. "
     "Causa: Partição EFI danificada ou partição de boot desconfigurada no disco GPT. "
     "Solução: Dê boot pelo pendrive de instalação, abra o CMD e reescreva a partição EFI utilizando o comando bcdboot C:\\Windows /l pt-br /s S: /f UEFI."),

    (28, "Configuração de inicialização limpa (Clean Boot) para isolar programas problemáticos", "Sistema Operacional",
     "Sintoma: Travamento esporádico sem causa aparente ao abrir aplicativos comuns. "
     "Causa: Serviços de terceiros em execução em segundo plano gerando sobrecarga. "
     "Solução: Execute msconfig, na aba Serviços marque 'Ocultar todos os serviços Microsoft' e clique em 'Desativar tudo'. Na aba Inicialização, desative itens no Gerenciador de Tarefas."),

    (29, "Como alterar a variável de ambiente PATH do sistema no Windows", "Sistema Operacional",
     "Sintoma: Comandos de ferramentas instaladas não são reconhecidos no terminal PowerShell/CMD. "
     "Causa: Binários não adicionados à variável PATH do sistema. "
     "Solução: Abra sysdm.cpl > Avançado > Variáveis de Ambiente. Na seção Variáveis do Sistema, edite 'Path' e adicione o caminho do executável."),

    (30, "Correção de congelamento da Barra de Tarefas e Menu Iniciar no Windows 11", "Sistema Operacional",
     "Sintoma: Clicar no botão Iniciar não abre o menu e a barra de tarefas não responde a cliques. "
     "Causa: Processo explorer.exe travado ou pacote StartMenuExperienceHost corrompido. "
     "Solução: No Gerenciador de Tarefas, localize o 'Windows Explorer', clique com o botão direito e selecione 'Reiniciar'."),

    (31, "Desbloqueio de unidade protegida por BitLocker solicitando chave de recuperação no boot", "Armazenamento",
     "Sintoma: Ao ligar o notebook o sistema trava na tela azul 'Digite a chave de recuperação do BitLocker'. "
     "Causa: Alteração na sequência de boot na BIOS ou atualização de firmware que limpou o registro do TPM. "
     "Solução técnica: Localize a chave numérica de 48 dígitos na conta corporativa do Microsoft Entra ID ou em https://account.microsoft.com/devices/recoverykey. "
     "Insira a chave para liberar a partição. Para suspender a exigência temporariamente durante manutenções, execute manage-bde -protectors -disable C:."),

    (32, "Como liberar espaço no disco local C: utilizando a Limpeza de Disco e Storage Sense", "Armazenamento",
     "Sintoma: Alerta de pouco espaço em disco impedindo atualizações e salvamento de arquivos. "
     "Causa: Acúmulo de arquivos temporários, logs do sistema e pasta Windows.old de versões anteriores. "
     "Solução: Execute cleanmgr /sageset:1 e selecione 'Limpar arquivos do sistema' para remover instalações antigas do Windows."),

    (33, "Erro de partição em formato RAW no disco externo ou pendrive", "Armazenamento",
     "Sintoma: O Windows solicita formatação ao conectar o dispositivo dizendo 'O volume não contém um sistema de arquivos reconhecido'. "
     "Causa: Tabela de partição corrompida devido à desconexão brusca do dispositivo sem ejeção segura. "
     "Solução: Abra o CMD como administrador e tente recuperar o sistema de arquivos com chkdsk E: /f. Caso persista, use o Diskpart para recriar a partição NTFS."),

    (34, "Como configurar e monitorar o status de saúde de SSDs com comando SMART", "Armazenamento",
     "Sintoma: Lentidão repentina na gravação de arquivos com pequenos travamentos do mouse. "
     "Causa: Desgaste de células de memória flash do SSD atingindo o limite de TBW (Total Bytes Written). "
     "Solução: Abra o PowerShell e execute wmic diskdrive get status para status preliminar ou instale o CrystalDiskInfo para analisar setores realocados."),

    (35, "Configuração de cotas de disco para usuários no Windows Server (FSRM)", "Armazenamento",
     "Sintoma: Usuários enchendo discos compartilhados do servidor com arquivos pesados. "
     "Causa: Ausência de limites de armazenamento configurados por diretório. "
     "Solução: Instale a função File Server Resource Manager (FSRM) e crie modelos de cota rígida (Hard Quota) limitando o consumo a 50GB por pasta de usuário."),

    (36, "Sincronização de arquivos travada no OneDrive for Business", "Armazenamento",
     "Sintoma: Ícone do OneDrive na barra de tarefas permanece com símbolo de sincronização infinito. "
     "Causa: Arquivo com caracteres especiais no nome ou cache local do cliente corrompido. "
     "Solução: Execute o comando %localappdata%\\Microsoft\\OneDrive\\onedrive.exe /reset para redefinir as configurações e reiniciar a sincronização."),

    (37, "Erro 'O arquivo ou pasta está corrompido e ilegível' no disco local", "Armazenamento",
     "Sintoma: Impossibilidade de abrir ou deletar determinada pasta de trabalho. "
     "Causa: Inconsistência na Master File Table (MFT) do NTFS. "
     "Solução: Execute chkdsk C: /scan no Prompt de Comando para escanear sem necessidade de reinicialização imediata."),

    (38, "Como expandir volume de disco C: utilizando espaço não alocado no Diskpart", "Armazenamento",
     "Sintoma: A opção 'Estender Volume' no Gerenciamento de Disco aparece desabilitada em cinza. "
     "Causa: O espaço não alocado não é adjacente à partição C. "
     "Solução: Use ferramentas de particionamento para mover a partição de recuperação ou utilize o utilitário de linha de comando diskpart: select volume C; extend."),

    (39, "Configuração de Backup do Windows e criação de Imagem do Sistema", "Armazenamento",
     "Sintoma: Necessidade de plano de recuperação contra ransomware ou perda de hardware. "
     "Causa: Falta de rotinas automatizadas de cópia de segurança em disco secundário. "
     "Solução: Acesse o Histórico de Arquivos no Painel de Controle e configure o backup regular das pastas de perfil em unidade de rede externa."),

    (40, "Desfragmentação e otimização de unidades HDD e comando TRIM para SSD", "Armazenamento",
     "Sintoma: Desempenho de leitura degradado ao longo do tempo. "
     "Causa: Fragmentação em discos rígidos mecânicos ou falta de execução do comando TRIM no SSD. "
     "Solução: Execute no PowerShell defrag C: /O para enviar o comando de otimização/TRIM adequado para o tipo de mídia."),

    (41, "Configuração do Windows Defender e exclusão de pastas seguras de desenvolvimento", "Segurança",
     "Sintoma: Compilações lentas em IDEs de desenvolvimento causadas por escaneamento em tempo real do antivírus. "
     "Causa: O Microsoft Defender Antivirus analisa todos os arquivos binários intermediários gerados. "
     "Solução: No aplicativo Segurança do Windows > Proteção contra vírus e ameaças > Gerenciar configurações > Exclusões, "
     "adicione a pasta do projeto ou processo aos itens excluídos do escaneamento."),

    (42, "Como isolar estação infectada por malware da rede corporativa", "Segurança",
     "Sintoma: Comportamento anômalo na máquina com tráfego suspeito na rede e alertas de segurança. "
     "Causa: Infecção por trojan ou tentativa de movimentação lateral de ransomware. "
     "Solução: Desconecte o cabo de rede e desative o Wi-Fi imediatamente. No portal Microsoft Defender for Endpoint, use a ação 'Isolate device'."),

    (43, "Aplicação de políticas de restrição de execução de scripts no PowerShell (ExecutionPolicy)", "Segurança",
     "Sintoma: Erro 'o arquivo script.ps1 não pode ser carregado porque a execução de scripts foi desabilitada neste sistema'. "
     "Causa: A política padrão do Windows é Restricted para evitar execução inadvertida de código não assinado. "
     "Solução: Para permitir scripts locais assinados, execute como Admin: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser."),

    (44, "Configuração de controle de acesso de usuários (UAC) e privilégios mínimos", "Segurança",
     "Sintoma: Usuários comuns instalando softwares não autorizados ou prompts de UAC em excesso. "
     "Causa: Contas de usuário configuradas com perfil de Administrador local. "
     "Solução: Rebaixe o tipo de conta para 'Usuário Padrão' em netplwiz e configure a política de UAC para solicitar credenciais administrativas."),

    (45, "Auditoria e bloqueio de portas vulneráveis no Windows Defender Firewall", "Segurança",
     "Sintoma: Scanner de vulnerabilidade apontando portas abertas desnecessárias na estação. "
     "Causa: Regras de firewall muito permissivas criadas por softwares instalados. "
     "Solução: Revise as Regras de Entrada no Firewall do Windows e remova regras que permitam tráfego para portas sensíveis como 445 e 139 a partir da internet."),

    (46, "Proteção contra adulteração (Tamper Protection) no Microsoft Defender", "Segurança",
     "Sintoma: Antivírus desativando sozinho sem permissão do administrador. "
     "Causa: Ataque de malware tentando modificar chaves de registro do Windows Defender. "
     "Solução: Garanta que a Proteção contra Violação esteja ativada na central de Segurança do Windows ou via política Intune."),

    (47, "Habilitação do recurso de Isolamento de Núcleo e Integridade da Memória (HVCI)", "Segurança",
     "Sintoma: Notificação do Windows informando que a integridade da memória está desativada. "
     "Causa: Presença de drivers antigos incompatíveis que violam o modelo de segurança de virtualização. "
     "Solução: Identifique drivers incompatíveis pelo Gerenciador de Dispositivos e ative em Segurança do Dispositivo > Isolamento de Núcleo."),

    (48, "Como revogar sessões ativas e tokens de login após suspeita de comprometimento de conta", "Segurança",
     "Sintoma: Usuário relatou acesso não autorizado aos seus e-mails corporativos. "
     "Causa: Roubo de token de sessão ou senha vazada. "
     "Solução: O administrador deve acessar o portal Microsoft Entra, selecionar o usuário e clicar em 'Revogar Sessões', além de forçar redefinição imediata de senha."),

    (49, "Bloqueio de portas USB e unidades de armazenamento removíveis via GPO", "Segurança",
     "Sintoma: Risco de exfiltração de dados confidenciais por pendrives não homologados. "
     "Causa: Falta de restrição de mídias removíveis nas estações de trabalho. "
     "Solução: No Editor de Gerenciamento de Política de Grupo, configure 'Todas as classes de armazenamento removível: Negar todo o acesso'."),

    (50, "Criptografia de arquivos e pastas com EFS (Encrypting File System) no NTFS", "Segurança",
     "Sintoma: Necessidade de proteger documentos locais mesmo em caso de acesso físico ao HD. "
     "Causa: Arquivos confidenciais armazenados em texto claro em computadores compartilhados. "
     "Solução: Clique com botão direito na pasta > Propriedades > Avançado > Marcar 'Criptografar o conteúdo para proteger os dados' e exporte o certificado de recuperação."),

    (51, "Outlook fecha sozinho ou trava na tela 'Carregando Perfil'", "Office & Produtividade",
     "Sintoma: O Microsoft Outlook não abre, congelando na inicialização com alto uso de CPU. "
     "Causa: Arquivo de dados OST/PST corrompido ou suplemento (add-in) de terceiros travado. "
     "Solução técnica: Execute o Outlook em modo de segurança pressionando Win + R e digitando outlook.exe /safe. "
     "Acesse Arquivo > Opções > Suplementos e desmarque suplementos COM desnecessários. "
     "Se o problema persistir, repare o arquivo de dados utilizando a ferramenta SCANPST.EXE localizada na pasta do Office."),

    (52, "Excel apresentando mensagem 'Memória insuficiente' ao abrir planilha pesada", "Office & Produtividade",
     "Sintoma: O aplicativo trava ou emite alerta de falta de recursos ao calcular fórmulas dinâmicas. "
     "Causa: Utilização da versão de 32 bits do Office limitada a 2GB de memória RAM. "
     "Solução: Desinstale o Office de 32 bits e instale o pacote Microsoft 365 na arquitetura de 64 bits para permitir endereçamento ilimitado de memória."),

    (53, "Impressora padrão alterando sozinha no Windows 10/11", "Office & Produtividade",
     "Sintoma: Documentos sendo enviados para a impressora errada ao mandar imprimir no Word. "
     "Causa: O recurso nativo do Windows que gerencia a impressora padrão baseado no último uso está ativado. "
     "Solução: Vá em Configurações > Bluetooth e Dispositivos > Impressoras e Scanners e desmarque a opção 'Deixar o Windows gerenciar minha impressora padrão'."),

    (54, "Fila de impressão travada com documentos em status 'Excluindo...' ou 'Imprimindo'", "Office & Produtividade",
     "Sintoma: Nenhum documento novo é impresso e a fila não aceita cancelamento. "
     "Causa: O serviço Spooler de Impressão (spoolsv.exe) entrou em deadlock com arquivos no cache. "
     "Solução: Abra o CMD como Admin e execute: net stop spooler. Apague todos os arquivos em C:\\Windows\\System32\\spool\\PRINTERS e reinicie com net start spooler."),

    (55, "Erro de ativação do Microsoft Office 'Produto Não Licenciado' no Microsoft 365", "Office & Produtividade",
     "Sintoma: Faixa amarela no topo do Word/Excel avisando que o produto não está licenciado. "
     "Causa: Licença corporativa expirada ou credenciais do Office travadas em cache. "
     "Solução: Execute o utilitário de suporte e recuperação da Microsoft (SaRA) ou limpe as licenças antigas com o script ospp.vbs /unpkey."),

    (56, "Como reparar a instalação do pacote Microsoft Office 365", "Office & Produtividade",
     "Sintoma: Aplicativos do Office fechando inesperadamente após atualização do Windows. "
     "Causa: DLLs compartilhadas do runtime do Office danificadas. "
     "Solução: Acesse Painel de Controle > Programas e Recursos, clique com botão direito em Microsoft 365 Apps > Alterar > Selecione 'Reparo Rápido' ou 'Reparo Online'."),

    (57, "Configuração de assinatura de e-mail automática no Microsoft Outlook", "Office & Produtividade",
     "Sintoma: Novos e-mails criados não incluem a assinatura padrão da empresa. "
     "Causa: Assinatura não vinculada à conta de e-mail correspondente nas preferências. "
     "Solução: No Outlook, acesse Arquivo > Opções > Email > Assinaturas. Selecione a conta e defina a assinatura para novas mensagens e respostas."),

    (58, "Recuperação de pasta de trabalho do Excel não salva após desligamento inesperado", "Office & Produtividade",
     "Sintoma: Perda de edições recentes devido a queda repentina de energia. "
     "Causa: Fechamento anômalo antes do salvamento manual. "
     "Solução: Abra o Excel, vá em Arquivo > Informações > Gerenciar Pasta de Trabalho > Recuperar Pastas de Trabalho Não Salvas."),

    (59, "Compartilhamento de calendário no Outlook com permissão de delegado", "Office & Produtividade",
     "Sintoma: Assistente não consegue agendar reuniões em nome do gestor. "
     "Causa: Ausência de permissão de representante no perfil Exchange. "
     "Solução: No Outlook, Arquivo > Configurações de Conta > Acesso de Representante. Adicione o usuário e selecione o nível de permissão 'Editor'."),

    (60, "Configuração do Microsoft Teams para iniciar automaticamente com o Windows", "Office & Produtividade",
     "Sintoma: Usuário perde chamadas no início do expediente por não ter aberto o comunicador. "
     "Causa: Inicialização automática desmarcada nas preferências do aplicativo. "
     "Solução: Nas Configurações do Teams > Geral, marque 'Inicialização automática do aplicativo' ou adicione o atalho na pasta shell:startup."),

    # 61 a 100: Novos tópicos Microsoft 100% autênticos
    (61, "Perfil de usuário temporário carregado após logon no Windows (You have been signed in with a temporary profile)", "Sistema Operacional",
     "Sintoma: O usuário faz login e seus arquivos da área de trabalho sumiram, recebendo o aviso de perfil temporário. "
     "Causa: Chave de registro corrompida em HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList terminando em .bak. "
     "Solução técnica: Acesse o Registro do Windows com conta de administrador. Localize a chave com extensão .bak na lista de perfis, "
     "remova a chave temporária sem .bak e renomeie a chave .bak removendo o sufixo. Reinicie o computador."),

    (62, "Falha de autenticação RDP com erro CredSSP Encryption Oracle Remediation", "Conectividade",
     "Sintoma: Erro ao conectar via Área de Trabalho Remota informando falha de correção de criptografia CredSSP. "
     "Causa: O computador cliente possui atualização de segurança mais recente que o servidor de destino desatualizado. "
     "Solução técnica: No Editor de Política de Grupo Local (gpedit.msc), navegue até Configuração do Computador > Modelos Administrativos > "
     "Sistema > Delegação de Credenciais > Correção de Criptografia do Oracle. Configure como 'Habilitado' com nível 'Vulnerável' temporariamente."),

    (63, "Windows Defender travando compilação do Visual Studio e dotnet build", "Segurança",
     "Sintoma: Compilações de projetos .NET demorando minutos a mais com alto uso de CPU pelo Antimalware Service Executable. "
     "Causa: Inspeção em tempo real de milhares de arquivos binários intermediários nas pastas obj e bin. "
     "Solução técnica: No aplicativo Segurança do Windows, adicione exclusões de processo para devenv.exe, msbuild.exe e dotnet.exe, "
     "além de excluir a pasta raiz do repositório de código-fonte."),

    (64, "Erro de tela azul DPC_WATCHDOG_VIOLATION no Windows 11", "Sistema Operacional",
     "Sintoma: Travamento completo do sistema operacional com BSOD código DPC_WATCHDOG_VIOLATION. "
     "Causa: Driver do controlador SATA/AHCI iaStorA.sys incompatível ou firmware de SSD NVMe desatualizado. "
     "Solução técnica: No Gerenciador de Dispositivos, expanda Controladores IDE ATA/ATAPI, selecione 'Atualizar driver', "
     "escolha 'Procurar drivers no computador' e selecione o 'Controlador SATA AHCI Padrão' nativo da Microsoft."),

    (65, "Serviço do Windows travado no status 'Parando' (Stopping) e não finaliza", "Sistema Operacional",
     "Sintoma: O serviço não conclui o desligamento e os botões Iniciar e Parar ficam desabilitados no services.msc. "
     "Causa: A thread principal do processo do serviço entrou em deadlock e parou de responder ao Service Control Manager (SCM). "
     "Solução técnica: Abra o CMD como Administrador e execute sc queryex nome_do_servico para identificar o PID. "
     "Em seguida force a finalização do processo com taskkill /f /pid <PID>."),

    (66, "Erro de ativação do Windows 0xC004C008 chave de produto já utilizada", "Sistema Operacional",
     "Sintoma: O Windows informa que a chave de produto não pode ser usada neste computador por atingir limite de ativações. "
     "Causa: Licença MAK corporativa esgotada ou reinstalação em placa-mãe substituída. "
     "Solução técnica: Abra o prompt de comando como Administrador e digite slui 4 para iniciar o assistente de ativação por telefone da Microsoft, "
     "ou insira a chave KMS institucional com slmgr.vbs /ipk <chave_kms> e ative com slmgr.vbs /ato."),

    (67, "Falha de sombra de cópia de volume VSS Writer ao executar backup corporativo (Erro 0x80042318)", "Armazenamento",
     "Sintoma: O software de backup emite erro informando que os componentes VSS falharam ao congelar o sistema de arquivos. "
     "Causa: Gravador VSS (VSS Writer) entrou em estado instável ou com falha. "
     "Solução técnica: Execute vssadmin list writers para identificar o gravador com status 'Failed'. "
     "Reinicie os serviços associados: Volume Shadow Copy (VSS) e Serviços Criptográficos (CryptSvc) via net stop cryptsvc && net start cryptsvc."),

    (68, "Erro de logon interativo: O servidor RPC não está disponível no Windows", "Conectividade",
     "Sintoma: Estação cliente não consegue validar logon no Active Directory com erro 'O servidor RPC não está disponível'. "
     "Causa: Bloqueio das portas TCP dinâmicas 49152-65535 ou serviço Chamada de Procedimento Remoto (RpcSs) parado no controlador. "
     "Solução técnica: Teste a comunicação de rede usando Test-NetConnection -ComputerName dc.empresa.local -Port 135. "
     "Certifique-se de que o serviço RPC e o Localizador RPC estejam em execução no Domain Controller."),

    (69, "Outlook atingiu o limite de tamanho do arquivo de dados OST de 50GB", "Office & Produtividade",
     "Sintoma: O Outlook para de receber novos e-mails e exibe mensagem 'O arquivo de dados atingiu o tamanho máximo'. "
     "Causa: Caixas de correio pesadas que ultrapassaram a cota padrão de 50GB para arquivos OST/PST no Office 365. "
     "Solução técnica: Abra o regedit e navegue até HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Outlook\\PST. "
     "Crie dois valores DWORD: MaxLargeFileSize (valor decimal 102400 para 100GB) e WarnLargeFileSize (valor decimal 97280 para 95GB)."),

    (70, "Erro 0x80240034 ao baixar atualização cumulativa no Windows Update", "Sistema Operacional",
     "Sintoma: O download da atualização trava em determinada porcentagem e acusa o código 0x80240034. "
     "Causa: Metadados corrompidos na fila do Background Intelligent Transfer Service (BITS). "
     "Solução técnica: Pare os serviços wuauserv e bits. Exclua os arquivos de fila em C:\\ProgramData\\Microsoft\\Network\\Downloader\\qmgr*.dat. "
     "Em seguida reinicie os serviços e force nova checagem pelo PowerShell com usoclient StartInteractiveScan."),

    (71, "Computador perde data e hora toda vez que é desligado da tomada", "Sistema Operacional",
     "Sintoma: Ao ligar o computador a data volta para anos anteriores (ex: 2000 ou 2015) e sites não abrem por erro de SSL. "
     "Causa: Bateria de lítio tipo moeda CR2032 da placa-mãe (responsável por manter o circuito RTC da BIOS) descarregada. "
     "Solução técnica: Efetue a troca física da bateria CR2032 na placa-mãe. Acesse o menu da BIOS/UEFI no primeiro boot "
     "para ajustar a hora correta e a ordem dos discos de inicialização."),

    (72, "Área de Trabalho Remota desconecta por falta de licenças de acesso para cliente (CAL RDS)", "Conectividade",
     "Sintoma: Usuário recebe a mensagem 'A sessão remota foi desconectada porque não há licenças de acesso disponíveis'. "
     "Causa: Esgotamento do período de carência (Grace Period) de 120 dias do Remote Desktop Licensing no servidor. "
     "Solução técnica: Abra o Gerenciador de Licenciamento da Área de Trabalho Remota (licmgr.exe), ative o servidor de licenças "
     "e instale o pacote de RDS CALs por Usuário adquirido junto ao programa de licenciamento da Microsoft."),

    (73, "Cursor do mouse congelando em intervalos regulares (micro-stuttering) no Windows", "Sistema Operacional",
     "Sintoma: O ponteiro do mouse trava a cada 2 ou 3 segundos durante navegação comum ou uso de planilhas. "
     "Causa: Polling rate do mouse muito elevado (1000Hz ou 8000Hz) gerando interrupções massivas na CPU ou conflito com software RGB. "
     "Solução técnica: No software do fabricante do periférico, reduza a taxa de comunicação (Polling Rate) para 500Hz ou 250Hz. "
     "No Painel de Controle de Mouse, desmarque 'Aprimorar precisão do ponteiro'."),

    (74, "Erro de permissão negada ao executar script .ps1 baixado da internet (Zone.Identifier)", "Segurança",
     "Sintoma: O PowerShell bloqueia o script informando que ele veio de outro computador e foi bloqueado para proteger o sistema. "
     "Causa: O fluxo de dados alternativo (Alternate Data Stream) Zone.Identifier marca o arquivo como originário da zona Internet. "
     "Solução técnica: Abra o PowerShell no diretório do arquivo e execute o comando: Unblock-File -Path .\\script_desejado.ps1, "
     "removendo a marcação de segurança de origem externa."),

    (75, "Tela preta após retornar do modo de suspensão ou hibernação no notebook", "Sistema Operacional",
     "Sintoma: O computador liga as ventoinhas mas a tela permanece preta após acordar da suspensão. "
     "Causa: Recurso de Inicialização Rápida (Fast Startup) incompatível com o driver Intel Management Engine Interface (IMEI). "
     "Solução técnica: Acesse Painel de Controle > Opções de Energia > 'Escolher a função dos botões de energia'. "
     "Clique em 'Alterar configurações não disponíveis no momento' e desmarque 'Ligar inicialização rápida (recomendado)'."),

    (76, "Falha ao mapear unidade de rede via script de logon (Nome de dispositivo local já em uso)", "Conectividade",
     "Sintoma: O comando net use falha com erro 85: 'O nome de dispositivo local já está em uso'. "
     "Causa: Letra de unidade (ex: Z:) retida por uma sessão de logon desconectada anteriormente. "
     "Solução técnica: Antes de mapear a unidade, adicione uma instrução de expurgo prévio: net use Z: /delete /yes. "
     "Em seguida reconecte com net use Z: \\\\servidor\\compartilhamento /persistent:no."),

    (77, "Sincronização do OneDrive pausada por arquivos com caracteres inválidos", "Armazenamento",
     "Sintoma: O ícone do OneDrive exibe uma cruz vermelha avisando que não pode sincronizar determinados itens. "
     "Causa: Pastas ou arquivos locais contendo caracteres reservados pelo protocolo NTFS/SharePoint (< > : \" / \\ | ? *). "
     "Solução técnica: Identifique os arquivos na lista de erros do OneDrive e renomeie-os removendo caracteres especiais. "
     "Evite terminar nomes de pastas com espaços ou pontos."),

    (78, "Erro no DISM 'Os arquivos de origem não puderam ser encontrados' (Error 0x800f081f)", "Sistema Operacional",
     "Sintoma: O comando DISM /RestoreHealth falha em 62.3% acusando falta de arquivos fonte de componentes. "
     "Causa: O repositório local WinSxS está corrompido e o Windows Update não conseguiu baixar os pacotes equivalentes. "
     "Solução técnica: Monte a imagem ISO oficial da mesma versão do Windows (ex: unidade D:) e aponte o arquivo install.wim: "
     "DISM /Online /Cleanup-Image /RestoreHealth /Source:WIM:D:\\sources\\install.wim:1 /LimitAccess."),

    (79, "Impressora de rede sumindo da lista de dispositivos após reiniciar a máquina", "Office & Produtividade",
     "Sintoma: Usuário precisa reinstalar a impressora todo dia porque ela desaparece ao reiniciar o Windows. "
     "Causa: Falha de comunicação no isolamento do processo do driver de impressão no spooler. "
     "Solução técnica: Abra o console de Gerenciamento de Impressão (printmanagement.msc), localize o driver da impressora, "
     "clique com botão direito e selecione 'Definir Isolamento de Driver' > 'Isolado'. Garanta a instalação de drivers do tipo V4."),

    (80, "Erro 'Falha na inicialização do serviço cliente de Política de Grupo' ao efetuar logon", "Autenticação",
     "Sintoma: Usuário padrão não consegue fazer login no computador com mensagem de erro do serviço gpsvc. "
     "Causa: Corrupção nas chaves de registro de registro do serviço gpsvc em HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Svchost. "
     "Solução técnica: Inicialize o Windows em Modo de Segurança com conta Administrador e recrie o grupo GPSvcGroup no registro "
     "associando AuthenticationCapabilities (DWORD 0x3020) e CoInitializeSecurityParam (DWORD 1)."),

    (81, "Pasta C:\\Windows\\Temp acumulando centenas de gigabytes de arquivos temporários cab_*", "Armazenamento",
     "Sintoma: O disco rígido C: enche repentinamente com milhares de arquivos cab_XXXX no diretório Windows\\Temp. "
     "Causa: O utilitário Makecab falha repetidamente ao compactar arquivos de log CBS (Component Based Servicing) maiores que 2GB. "
     "Solução técnica: Abra C:\\Windows\\Logs\\CBS, localize o arquivo CbsPersist_*.log com mais de 2GB e mova-o ou delete-o. "
     "Em seguida apague com segurança todos os arquivos cab_* acumulados em C:\\Windows\\Temp."),

    (82, "Erro de tela azul KERNEL_SECURITY_CHECK_FAILURE durante uso intenso", "Sistema Operacional",
     "Sintoma: Travamento súbito do sistema com código de erro KERNEL_SECURITY_CHECK_FAILURE (0x00000139). "
     "Causa: Corrupção de estruturas de dados do kernel causada por pente de memória RAM defeituoso ou overclock instável. "
     "Solução técnica: Execute o Diagnóstico de Memória do Windows pressionando Win + R e digitando mdsched.exe. "
     "Seletione 'Reiniciar agora e verificar se há problemas'. Remova perfis XMP/DOCP instáveis na BIOS."),

    (83, "Certificado de segurança corporativo não confiável no navegador Edge/Chrome", "Segurança",
     "Sintoma: Navegador exibe tela vermelha 'Sua conexão não é particular' (NET::ERR_CERT_AUTHORITY_INVALID) em sistemas internos. "
     "Causa: A Autoridade Certificadora Raiz interna da empresa não foi distribuída para o repositório confiável do computador. "
     "Solução técnica: Abra o certmgr.msc no Windows, navegue até 'Autoridades de Certificação Raiz Confiáveis' > 'Certificados'. "
     "Importe o arquivo do certificado raiz (.cer ou .crt) corporativo marcando a opção de confiar na autoridade."),

    (84, "Falha ao inicializar o Hyper-V com mensagem 'O hipervisor não está em execução'", "Sistema Operacional",
     "Sintoma: Máquinas virtuais não iniciam no Hyper-V com erro 'Hypervisor is not running'. "
     "Causa: A tecnologia de virtualização de hardware (VT-x ou AMD-V) está desativada na BIOS ou o hipervisor não foi marcado para boot. "
     "Solução técnica: Habilite a virtualização de hardware no menu UEFI/BIOS da placa-mãe. "
     "No prompt de comando como Administrador, execute bcdedit /set hypervisorlaunchtype auto e reinicie."),

    (85, "Áudio não sai pelo fone de ouvido conectado na entrada P2 frontal do gabinete", "Sistema Operacional",
     "Sintoma: O som continua saindo pelos alto-falantes mesmo com o fone plugado na porta frontal. "
     "Causa: Detecção de conector frontal (Jack Detection) desabilitada ou desconfigurada no driver Realtek HD Audio. "
     "Solução técnica: Abra o Painel de Controle Realtek Audio Console, acesse as opções avançadas do conector "
     "e marque 'Desativar a detecção do conector do painel frontal' para forçar o chaveamento de saída."),

    (86, "Erro 0x80070005 (Acesso Negado) ao tentar instalar aplicativo da Microsoft Store", "Office & Produtividade",
     "Sintoma: O download é concluído na Microsoft Store mas a instalação aborta com erro 0x80070005. "
     "Causa: Permissões de segurança corrompidas na pasta oculta C:\\Program Files\\WindowsApps. "
     "Solução técnica: Pressione Win + R, digite wsreset.exe e aguarde o término do reset do cache da loja. "
     "Abra o PowerShell como Admin e registre novamente os pacotes com Get-AppXPackage *WindowsStore* -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}."),

    (87, "Gerenciador de Tarefas não abre ao pressionar Ctrl + Shift + Esc", "Sistema Operacional",
     "Sintoma: O Windows emite mensagem 'O Gerenciador de Tarefas foi desativado pelo administrador'. "
     "Causa: Chave de registro restritiva criada por malware ou política de grupo (DisableTaskMgr). "
     "Solução técnica: Abra o Prompt de Comando como Administrador e execute: "
     "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /f."),

    (88, "Erro de tela preta com cursor do mouse após atualização cumulativa do Windows", "Sistema Operacional",
     "Sintoma: O computador conclui a reinicialização da atualização mas entra em tela preta exibindo apenas o ponteiro do mouse. "
     "Causa: Falha de inicialização do processo shell explorer.exe devido a conflito de driver de vídeo. "
     "Solução técnica: Pressione Ctrl + Shift + Esc para abrir o Gerenciador de Tarefas. Vá em Arquivo > Executar nova tarefa, "
     "digite explorer.exe e marque 'Criar esta tarefa com privilégios administrativos'. Atualize o driver gráfico em seguida."),

    (89, "Conexão de rede Wi-Fi corporativa 802.1X desconectando a cada 10 minutos", "Conectividade",
     "Sintoma: O notebook autentica na rede WPA2-Enterprise com certificado ou PEAP mas desconecta regularmente em poucos minutos. "
     "Causa: O temporizador de reautenticação periódica EAPOL (Session-Timeout) no servidor RADIUS está muito curto. "
     "Solução técnica: Nas propriedades da conexão de rede sem fio corporativa > Segurança > Configurações Avançadas, "
     "habilite o modo de logon único (SSO) e marque 'Habilitar retenção de chave de par rápido (PMK Cache)'."),

    (90, "Área de Transferência compartilhada (Cloud Clipboard / Win + V) não sincroniza histórico", "Office & Produtividade",
     "Sintoma: Ao pressionar Win + V o menu de múltiplos itens copiados aparece vazio ou desativado. "
     "Causa: O serviço de histórico da Área de Transferência foi desativado nas preferências de privacidade ou via GPO. "
     "Solução técnica: Acesse Configurações > Sistema > Área de Transferência e ative a opção 'Histórico da área de transferência'. "
     "Verifique se o serviço 'Serviço de Roteamento de Mensagens Por Push do WAP' (dmwappushservice) está ativo."),

    (91, "Disco rígido externo não recebe letra de unidade no Windows Explorer", "Armazenamento",
     "Sintoma: O pendrive ou HD externo emite som de conexão USB e aparece no Gerenciador de Dispositivos, mas não abre no Explorador de Arquivos. "
     "Causa: O recurso de montagem automática de novas unidades (Automount) do Windows foi desabilitado. "
     "Solução técnica: Abra o CMD como Administrador e abra o diskpart. Execute automount enable. "
     "Em seguida selecione o volume com list volume; select volume X; assign letter=G."),

    (92, "Erro 'Esta cópia do Windows não é original' exibido após atualização de BIOS", "Sistema Operacional",
     "Sintoma: Marca d'água no canto inferior direito informando 'Ativar o Windows' após atualizar a firmware da placa-mãe. "
     "Causa: A atualização de BIOS limpou a chave de ativação digital OEM gravada na tabela MSDM da ACPI. "
     "Solução técnica: No PowerShell como Administrador execute (Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey "
     "para resgatar a chave original gravada no chip e reaplique-a com slmgr.vbs /ipk <chave_encontrada>."),

    (93, "Microsoft Teams não detecta microfone do fone de ouvido Bluetooth", "Office & Produtividade",
     "Sintoma: O usuário consegue ouvir a reunião mas o microfone não capta áudio nas chamadas do Teams. "
     "Causa: O Windows configurou o dispositivo apenas como fone estéreo de saída em vez de headset de comunicação bidirecional Hands-Free. "
     "Solução técnica: Em Configurações de Som > Mais configurações de som > aba Gravação, localize o dispositivo 'Headset Hands-Free AG Audio', "
     "clique com o botão direito e marque 'Definir como Dispositivo Padrão' e 'Definir como Dispositivo de Comunicação Padrão'."),

    (94, "Lixeira corrompida na unidade C: impedindo exclusão de arquivos (A Lixeira em C: está corrompida)", "Armazenamento",
     "Sintoma: Ao tentar deletar um arquivo o sistema exibe pop-up informando que a Lixeira está corrompida e pergunta se deseja esvaziá-la. "
     "Causa: Arquivo de metadados $I ou pasta oculta $Recycle.Bin com permissões ou setores inconsistentes. "
     "Solução técnica: Abra o Prompt de Comando como Administrador e execute rd /s /q C:\\$Recycle.bin. "
     "O Windows recriará uma nova estrutura de Lixeira limpa e funcional automaticamente."),

    (95, "Erro 'O arquivo de dados do Outlook atingiu o tamanho máximo' ao receber novos emails", "Office & Produtividade",
     "Sintoma: Não é possível mover ou receber novas mensagens em contas POP3/IMAP antigas. "
     "Causa: O arquivo .pst foi criado no formato antigo ANSI (Office 97-2002) que possui limite rígido de 2GB de capacidade. "
     "Solução técnica: Crie um novo arquivo de dados do Outlook (.pst) no formato moderno Unicode (suporta até 50GB). "
     "Copie os dados das pastas antigas para o novo arquivo e torne-o o arquivo de entrega padrão."),

    (96, "Computador reinicia sozinho durante a noite sem aviso fechando arquivos abertos", "Sistema Operacional",
     "Sintoma: O colaborador deixa documentos em edição abertos e encontra o computador reiniciado na manhã seguinte. "
     "Causa: Política padrão do Windows Update que força reinicialização fora do 'Horário de Atividade' para aplicar patches. "
     "Solução técnica: No Editor de Política de Grupo (gpedit.msc), acesse Configuração do Computador > Modelos Administrativos > "
     "Componentes do Windows > Windows Update e habilite 'Não reiniciar automaticamente para atualizações agendadas se houver usuários conectados'."),

    (97, "Erro de certificado SSL/TLS no PowerShell ao invocar Invoke-WebRequest", "Segurança",
     "Sintoma: Scripts de automação do PowerShell falham com erro 'A solicitação foi anulada: Não foi possível criar um canal seguro para SSL/TLS'. "
     "Causa: O Windows PowerShell 5.1 utiliza por padrão protocolos legados SSLv3/TLS 1.0 para requisições HTTPS. "
     "Solução técnica: Adicione a seguinte linha no início do script de automação para forçar o uso de TLS 1.2 moderno: "
     "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12."),

    (98, "Uso excessivo de CPU pelo processo WmiPrvSE.exe (Host do Provedor WMI)", "Sistema Operacional",
     "Sintoma: O processo WmiPrvSE consome continuamente entre 30% e 50% de uso de CPU deixando o computador lento. "
     "Causa: Aplicativo de monitoramento de terceiros fazendo consultas WMI mal otimizadas ou com vazamento de chamadas. "
     "Solução técnica: Abra o Visualizador de Eventos > Logs de Aplicativos e Serviços > Microsoft > Windows > WMI-Activity > Operational. "
     "Localize os eventos de erro 5858 e verifique o campo ClientProcessId para identificar e finalizar o aplicativo ofensor."),

    (99, "Menu de contexto de clique direito com lentidão de vários segundos para abrir no Explorer", "Sistema Operacional",
     "Sintoma: Ao clicar com o botão direito do mouse sobre qualquer arquivo na Área de Trabalho a tela congela por 4 segundos. "
     "Causa: Extensão de shell adicionada por software de terceiros desinstalado incorretamente tentando consultar recursos inexistentes. "
     "Solução técnica: Baixe o utilitário gratuito ShellExView da NirSoft. Filtre as extensões de contexto que não pertencem à Microsoft "
     "e desative-as uma a uma para identificar o item causador do atraso."),

    (100, "Erro 'Não foi possível carregar o arquivo ou assembly' em programas legados .NET", "Office & Produtividade",
     "Sintoma: Software corporativo de gestão não inicializa acusando dependência ausente do .NET Framework 3.5. "
     "Causa: As versões recentes do Windows 10 e 11 vêm apenas com .NET 4.8 e .NET 8 habilitados por padrão. "
     "Solução técnica: Abra o PowerShell como Administrador e instale o runtime legado executando: "
     "Enable-WindowsOptionalFeature -Online -FeatureName NetFx3 -All.")
]

# =====================================================================
# CENÁRIO B: 100 DOCUMENTOS UBUNTU AUTÊNTICOS E DISTINTOS (IDs 101-200)
# =====================================================================
ub_docs_raw = [
    (101, "Como reparar dependências quebradas no APT e travas do dpkg no Ubuntu", "Gerenciamento de Pacotes",
     "Sintoma: Erro 'E: Could not get lock /var/lib/dpkg/lock-frontend' ou 'dpkg was interrupted'. "
     "Causa: Interrupção forçada durante atualização do sistema ou processo de atualização rodando em segundo plano. "
     "Solução técnica: Verifique se há processos do apt ativos com ps aux | grep -i apt. Se nenhum processo legítimo estiver ativo, "
     "remova os arquivos de trava com: sudo rm /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock*. "
     "Em seguida reconfigure pacotes pendentes e corrija dependências quebradas: "
     "1. sudo dpkg --configure -a "
     "2. sudo apt-get install -f "
     "3. sudo apt update && sudo apt clean."),

    (102, "Configuração de rede estática e resolução DNS utilizando o Netplan no Ubuntu 22.04/24.04", "Conectividade",
     "Sintoma: O servidor Ubuntu perdeu o endereço IP após reiniciar ou não resolve nomes de domínio externos. "
     "Causa: Arquivo de configuração YAML do Netplan desconfigurado ou com indentação de espaços inválida. "
     "Solução técnica: Edite o arquivo em /etc/netplan/01-netcfg.yaml e garanta indentação estrita de 2 espaços: "
     "network: version: 2 ethernets: eth0: dhcp4: no addresses: [192.168.1.50/24] routes: - to: default via: 192.168.1.1 "
     "nameservers: addresses: [8.8.8.8, 1.1.1.1]. Em seguida teste e aplique com: sudo netplan try e sudo netplan apply."),

    (103, "Recuperação do gerenciador de boot GRUB ausente ou quebrado após atualização", "Sistema Operacional",
     "Sintoma: O computador liga e cai diretamente no prompt 'grub rescue>' ou não carrega a lista de kernels. "
     "Causa: MBR ou partição EFI corrompida durante atualização do kernel ou instalação em dual-boot. "
     "Solução: Inicialize via Live USB do Ubuntu. Abra o terminal e execute: sudo add-apt-repository ppa:yannubuntu/boot-repair, "
     "sudo apt update e sudo apt install boot-repair. Execute boot-repair e selecione 'Recommended repair' para reinstalar o GRUB na partição correta."),

    (104, "Como diagnosticar e resolver alta carga de CPU e uso de memória com htop e systemd-cgtop", "Sistema Operacional",
     "Sintoma: Sistema travando, cursor do mouse com lentidão severa e carga (load average) acima do número de núcleos de CPU. "
     "Causa: Processo desgovernado com vazamento de memória (memory leak) ou loops de threads infinitos. "
     "Solução: Utilize htop para visualizar processos por consumo de CPU/Memória. Identifique o PID problemático e execute kill -15 PID "
     "para término suave ou kill -9 PID em caso de recusa. Inspecione logs do processo via journalctl -u servico -e."),

    (105, "Serviço SSH falha ao iniciar na porta 22 (Connection refused / Connection timed out)", "Conectividade",
     "Sintoma: Administrador não consegue conectar remotamente via PuTTY ou terminal ao servidor Ubuntu. "
     "Causa: O daemon sshd está parado ou o firewall UFW bloqueou a porta padrão 22. "
     "Solução técnica: No console local da máquina, verifique o status com sudo systemctl status ssh. "
     "Se o serviço estiver parado, execute sudo systemctl start ssh && sudo systemctl enable ssh. "
     "No firewall nativo, libere a porta executando sudo ufw allow 22/tcp e sudo ufw reload."),

    (106, "Disco cheio no Ubuntu: como identificar e limpar arquivos grandes em /var/log e cache do apt", "Armazenamento",
     "Sintoma: Erro 'No space left on device' impedindo criação de arquivos, banco de dados travando. "
     "Causa: Logs rotacionados acumulados em /var/log/journal ou cache gigante em /var/cache/apt. "
     "Solução: Execute df -h para verificar a partição afetada. Localize diretórios consumidores com sudo du -sh /* 2>/dev/null | sort -h. "
     "Limpe logs antigos do systemd com sudo journalctl --vacuum-time=3d e o cache de pacotes com sudo apt clean && sudo apt autoremove --purge."),

    (107, "Como configurar e montar partições automaticamente no /etc/fstab", "Armazenamento",
     "Sintoma: O segundo disco rígido ou partição de dados não aparece após o reboot do sistema. "
     "Causa: Falta de entrada correspondente com o UUID correto no arquivo de tabela de sistemas de arquivos /etc/fstab. "
     "Solução: Identifique o UUID do volume usando sudo blkid. Crie o ponto de montagem com sudo mkdir -p /dados. "
     "Adicione a linha em /etc/fstab: UUID=xxxx-xxxx /dados ext4 defaults 0 2. Teste a sintaxe sem reiniciar com sudo mount -a."),

    (108, "Permissão negada (Permission denied) em pastas compartilhadas e gestão de usuários/grupos", "Segurança",
     "Sintoma: Desenvolvedor ou usuário comum não consegue ler ou gravar arquivos dentro de /var/www ou /opt. "
     "Causa: Proprietário (owner) ou permissões POSIX restritas sem associação do usuário ao grupo correto. "
     "Solução: Adicione o usuário ao grupo responsável com sudo usermod -aG www-data $USER. "
     "Ajuste a propriedade e permissões recursivamente com sudo chown -R $USER:www-data /var/www e sudo chmod -R 775 /var/www."),

    (109, "Firewall UFW no Ubuntu: regras básicas de segurança e proteção de portas abertas", "Segurança",
     "Sintoma: Serviços expostos indevidamente para a rede pública sofrendo tentativas de invasão. "
     "Causa: Firewall local desativado por padrão na instalação limpa do Ubuntu. "
     "Solução: Ative o firewall definindo políticas seguras: sudo ufw default deny incoming, sudo ufw default allow outgoing. "
     "Habilite portas específicas com sudo ufw allow 80/tcp, sudo ufw allow 443/tcp e ative com sudo ufw enable."),

    (110, "Wi-Fi não funciona no notebook com Ubuntu: instalando drivers proprietários Broadcom/Realtek", "Conectividade",
     "Sintoma: O menu de configurações de rede não lista nenhuma rede sem fio disponível. "
     "Causa: Chipset Wi-Fi requer firmware proprietário não incluso no kernel genérico open-source. "
     "Solução: Conecte via cabo Ethernet. Abra 'Programas e Atualizações' > aba 'Drivers Adicionais'. "
     "Selecione o driver proprietário correspondente (ex: bcmwl-kernel-source) e clique em 'Aplicar alterações', ou instale via terminal."),

    (111, "Gerenciamento de serviços com systemctl e visualização de logs com journalctl", "Serviços & Daemons",
     "Sintoma: Um serviço web (Nginx/Apache) falhou silenciosamente e não atende requisições. "
     "Causa: Erro de configuração na inicialização do daemon. "
     "Solução técnica: Verifique o estado do serviço com sudo systemctl status nginx. "
     "Para reiniciar execute sudo systemctl restart nginx. Para inspecionar os erros em tempo real execute sudo journalctl -u nginx -f -n 50."),

    (112, "Configuração de tarefas agendadas automáticas utilizando o Cron no Ubuntu", "Serviços & Daemons",
     "Sintoma: O script de backup noturno não é disparado automaticamente. "
     "Causa: Sintaxe inválida no crontab ou ausência de variáveis de ambiente no shell de execução do cron. "
     "Solução: Edite o agendador com crontab -e. Adicione horários utilizando a convenção (minuto hora dia mês dia-semana): "
     "0 3 * * * /usr/bin/python3 /scripts/backup.py >> /var/log/backup.log 2>&1. Certifique-se de usar caminhos absolutos para binários."),

    (113, "Recuperação de senha de usuário root ou administrador via Modo de Recuperação (GRUB)", "Segurança",
     "Sintoma: O administrador esqueceu a senha de root e do usuário sudo no servidor físico. "
     "Causa: Perda de credenciais de acesso local. "
     "Solução: Reinicie o servidor mantendo pressionada a tecla Shift para abrir o menu GRUB. "
     "Selecione 'Advanced options for Ubuntu' > 'Recovery mode' > 'root Drop to root shell prompt'. "
     "Remonte a partição raiz em modo leitura/escrita com mount -o remount,rw / e altere com passwd seu_usuario."),

    (114, "Configuração e ativação de memória SWAP no Ubuntu para evitar encerramento por OOM Killer", "Armazenamento",
     "Sintoma: Banco de dados ou servidor web é morto subitamente com mensagem 'Out of memory: Kill process'. "
     "Causa: Esgotamento da memória RAM física sem área de troca (swap) configurada no disco. "
     "Solução técnica: Crie um arquivo de swap de 4GB com: sudo fallocate -l 4G /swapfile. "
     "Defina permissões estritas: sudo chmod 600 /swapfile. Formate e ative: sudo mkswap /swapfile && sudo swapon /swapfile. "
     "Torne permanente adicionando em /etc/fstab: /swapfile none swap sw 0 0."),

    (115, "Resolução de congelamento de tela e travamento gráfico em placas NVIDIA", "Sistema Operacional",
     "Sintoma: Tela preta com cursor piscando ou congelamento após suspender o computador. "
     "Causa: Conflito entre o driver open-source Nouveau e os módulos do driver proprietário NVIDIA. "
     "Solução: No terminal tty (Ctrl + Alt + F3), purgue drivers antigos com sudo apt-get purge nvidia*. "
     "Instale a versão estável recomendada pelo utilitário ubuntu-drivers install e reinicie o computador."),

    (116, "Instalação e configuração segura do Docker CE e Docker Compose no Ubuntu", "Serviços & Daemons",
     "Sintoma: Erro 'permission denied while trying to connect to the Docker daemon socket'. "
     "Causa: O usuário atual não possui permissão para acessar o socket Unix /var/run/docker.sock. "
     "Solução: Crie o grupo docker se não existir e adicione seu usuário: sudo usermod -aG docker $USER. "
     "Faça logout e login novamente para aplicar a nova associação de grupos."),

    (117, "Kernel Panic no boot do Ubuntu após atualização com comando apt upgrade", "Sistema Operacional",
     "Sintoma: Máquina não inicializa, luzes de Caps Lock piscando e erro 'Kernel panic - not syncing: VFS: Unable to mount root fs'. "
     "Causa: Imagem initramfs incompleta ou incompatibilidade com o kernel Linux mais recente. "
     "Solução: No menu GRUB, escolha 'Advanced options' e selecione o kernel estável imediatamente anterior. "
     "Após inicializar com sucesso, remova o kernel com defeito e recrie o initramfs com sudo update-initramfs -u -k all."),

    (118, "Como alterar o fuso horário (Timezone) e sincronizar NTP com timedatectl", "Sistema Operacional",
     "Sintoma: Horário das mensagens de logs com defasagem de 3 horas em relação ao horário local. "
     "Causa: Fuso horário configurado como UTC e serviço de sincronização systemd-timesyncd desativado. "
     "Solução: Configure o fuso horário brasileiro com sudo timedatectl set-timezone America/Sao_Paulo. "
     "Verifique a sincronização com timedatectl status."),

    (119, "Diagnóstico de lentidão de disco com iostat e iotop", "Armazenamento",
     "Sintoma: O sistema fica responsivo mas comandos de leitura/escrita travam o terminal. "
     "Causa: Processo efetuando escrita massiva saturando a fila de I/O do disco. "
     "Solução: Instale o sysstat com sudo apt install sysstat iotop. Execute sudo iotop -o para ver apenas os processos ativos consumindo I/O."),

    (120, "Como habilitar e configurar conexões SSH com par de chaves públicas/privadas RSA/Ed25519", "Segurança",
     "Sintoma: Necessidade de banir logins por senha simples para evitar ataques de força bruta no SSH. "
     "Causa: Acesso SSH configurado com PasswordAuthentication yes exposto na internet. "
     "Solução: Copie sua chave com ssh-copy-id usuario@servidor. No servidor, edite /etc/ssh/sshd_config, "
     "configure PasswordAuthentication no e PubkeyAuthentication yes. Reinicie o serviço com sudo systemctl restart ssh."),

    # 121 a 200: Novos tópicos Ubuntu 100% autênticos
    (121, "Erro 'The following signatures couldn't be verified: NO_PUBKEY' no apt update", "Gerenciamento de Pacotes",
     "Sintoma: Ao atualizar repositórios o apt exibe mensagem de erro de chave pública ausente com código hexadecimal da chave. "
     "Causa: Repositório de terceiro adicionado sem importar a respectiva assinatura digital GPG. "
     "Solução técnica: Importe a chave pública utilizando o comando: "
     "sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys <CODIGO_HEXADECIMAL>, "
     "ou exporte o arquivo .gpg para o diretório /etc/apt/trusted.gpg.d/."),

    (122, "Servidor Ubuntu inacessível na rede após alteração de IP com erro 'Network is unreachable'", "Conectividade",
     "Sintoma: Servidor não atinge internet nem outras sub-redes, emitindo 'Network is unreachable' em comandos ping ou curl. "
     "Causa: Falta de rota padrão (Default Gateway) configurada na tabela de roteamento do kernel. "
     "Solução técnica: Verifique a tabela com ip route show. Adicione a rota padrão com: "
     "sudo ip route add default via 192.168.1.1 dev eth0 e configure a seção routes no arquivo /etc/netplan/*.yaml."),

    (123, "Recuperação de imagem initramfs corrompida em modo de emergência (initramfs prompt)", "Sistema Operacional",
     "Sintoma: O boot do Ubuntu interrompe em tela preta com prompt '(initramfs)' sem carregar o sistema. "
     "Causa: Desligamento brusco corrompendo blocos da partição raiz que requer verificação manual de integridade. "
     "Solução técnica: No prompt de emergência, execute fsck /dev/sda1 -y (substituindo pela partição raiz). "
     "Após a conclusão dos reparos de nós de índice e blocos livres, digite exit ou reboot."),

    (124, "Partição ext4 montada como somente leitura (Read-only file system) após erro de I/O", "Armazenamento",
     "Sintoma: Impossível criar, editar arquivos ou iniciar serviços recebendo 'Read-only file system'. "
     "Causa: O driver ext4 detectou erros de consistência de metadados e protegeu o disco contra corrupção. "
     "Solução técnica: Desmonte o volume afetado com sudo umount /dados (ou remonte em leitura com mount -o remount,ro /dados). "
     "Execute o reparo profundo com sudo fsck.ext4 -fy /dev/sdb1 e remonte com sudo mount /dados."),

    (125, "Como rastrear qual processo está ocupando determinada porta de rede no Ubuntu (ss e lsof)", "Segurança",
     "Sintoma: Erro 'Address already in use' ao tentar subir uma aplicação ou container Docker. "
     "Causa: Outro serviço local já está vinculado à mesma porta TCP/UDP. "
     "Solução técnica: Execute sudo ss -tulpn | grep :8080 ou sudo lsof -i :8080 para identificar o PID do processo. "
     "Inspecione o programa com ps -p <PID> -o comm= e encerre-o com kill -15 <PID> caso necessário."),

    (126, "Serviço no systemd falhando com erro 'Start request repeated too quickly' (CrashLoop)", "Serviços & Daemons",
     "Sintoma: O serviço tenta subir continuamente, falha imediatamente e é bloqueado pelo systemd por excesso de tentativas. "
     "Causa: Erro de sintaxe no arquivo de configuração do aplicativo ou arquivo de banco de dados inacessível. "
     "Solução técnica: Inspecione a causa exata com sudo journalctl -u meu_servico.service -n 50 -e. "
     "No arquivo de unidade /etc/systemd/system/meu_servico.service ajuste RestartSec=5s para evitar rajada e recarregue com systemctl daemon-reload."),

    (127, "Espaço em disco 100% cheio no df -h mas du -sh não encontra arquivos grandes", "Armazenamento",
     "Sintoma: O comando df -h acusa partição / 100% ocupada, mas a soma dos arquivos com du -sh mostra pouco espaço utilizado. "
     "Causa: Arquivos volumosos de log foram excluídos com rm enquanto um processo ainda mantinha seu descritor de arquivo aberto. "
     "Solução técnica: Localize arquivos deletados retidos em memória com: sudo lsof +L1 ou sudo lsof | grep deleted. "
     "Reinicie o serviço correspondente listado para que o kernel libere os blocos de disco."),

    (128, "Erro 'No space left on device' mesmo tendo espaço livre em gigabytes no disco (Inodes esgotados)", "Armazenamento",
     "Sintoma: Falha ao salvar novos arquivos acusando falta de espaço, embora df -h mostre mais de 50GB livres. "
     "Causa: Esgotamento da tabela de nós de índice (inodes) do sistema de arquivos ext4 devido a milhões de arquivos minúsculos. "
     "Solução técnica: Verifique o uso de inodes com df -i. Identifique o diretório com excesso de arquivos com: "
     "find / -xdev -printf '%h\\n' | sort | uniq -c | sort -k 1 -n | tail -20 e remova arquivos órfãos de cache/sessões."),

    (129, "Usuário perdeu privilégios de sudo com erro '/etc/sudoers is world writable'", "Segurança",
     "Sintoma: Nenhum comando com sudo funciona, exibindo erro grave informando que /etc/sudoers tem permissão de escrita para todos. "
     "Causa: Execução acidental de chmod 777 recursivo na raiz ou na pasta /etc. "
     "Solução técnica: Utilize o utilitário pkexec (PolicyKit) para restaurar as permissões sem precisar reiniciar: "
     "pkexec chmod 0440 /etc/sudoers && pkexec chown root:root /etc/sudoers."),

    (130, "Erro 'Host key verification failed' ao tentar conectar em servidor SSH conhecido", "Segurança",
     "Sintoma: O cliente SSH recusa a conexão avisando 'WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!'. "
     "Causa: O servidor remoto foi reinstalado ou teve suas chaves criptográficas de host regeneradas, divergindo do arquivo local. "
     "Solução técnica: Remova a entrada antiga da chave no cliente utilizando o comando: "
     "ssh-keygen -f \"~/.ssh/known_hosts\" -R \"192.168.1.100\" e reconecte confirmando a nova impressão digital (fingerprint)."),

    (131, "Nginx falha ao reiniciar acusando erro de sintaxe nos blocos de configuração", "Serviços & Daemons",
     "Sintoma: O comando systemctl restart nginx falha e o site corporativo sai do ar. "
     "Causa: Falta de ponto-e-vírgula (;) ou chaves desbalanceadas nos arquivos de /etc/nginx/sites-available/. "
     "Solução técnica: Antes de reiniciar o servidor, valide sempre a integridade dos arquivos executando sudo nginx -t. "
     "O comando apontará o arquivo e a linha exata do erro de sintaxe para correção."),

    (132, "Configuração de rotação diária de logs corporativos pesados com Logrotate", "Serviços & Daemons",
     "Sintoma: Arquivos de log de aplicações personalizadas crescendo indefinidamente em /var/log/ e consumindo todo o disco. "
     "Causa: Falta de regra no utilitário de rotação logrotate para gerenciar arquivos de log de software próprio. "
     "Solução técnica: Crie o arquivo /etc/logrotate.d/minha_app contendo: "
     "/var/log/minha_app/*.log { daily missingok rotate 14 compress delaycompress notifempty create 0640 www-data adm }."),

    (133, "Erro 'Temporary failure in name resolution' após atualização do systemd-resolved", "Conectividade",
     "Sintoma: O sistema não consegue resolver nenhum domínio externo em comandos apt, curl ou ping. "
     "Causa: O link simbólico /etc/resolv.conf foi quebrado ou não aponta para o resolvedor stub local 127.0.0.53. "
     "Solução técnica: Recrie o link simbólico oficial do systemd executando: "
     "sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf && sudo systemctl restart systemd-resolved."),

    (134, "Aviso interativo 'needrestart' interrompendo atualizações em scripts automatizados do apt", "Gerenciamento de Pacotes",
     "Sintoma: Scripts de CI/CD ou updates em lote travam esperando confirmação de reinicialização de daemons em tela azul ncurses. "
     "Causa: O pacote needrestart vem configurado em modo interativo por padrão no Ubuntu 22.04 e 24.04. "
     "Solução técnica: Edite /etc/needrestart/needrestart.conf e configure $nrconf{restart} = 'a'; (automático) "
     "ou exporte a variável de ambiente DEBIAN_FRONTEND=noninteractive nos scripts."),

    (135, "Docker não consegue criar containers com erro 'driver failed programming external connectivity'", "Serviços & Daemons",
     "Sintoma: O comando docker run falha ao tentar mapear portas com erro de programação de conectividade externa. "
     "Causa: A tabela de regras iptables do Docker foi purgada após reinicialização do firewall UFW ou reload do iptables. "
     "Solução técnica: Reinicie o daemon do Docker para reconstruir as regras e cadeias nativas com: "
     "sudo systemctl restart docker."),

    (136, "Processos zumbis (defunct) acumulando na tabela de processos do Linux", "Sistema Operacional",
     "Sintoma: O comando top ou ps exibe dezenas de processos marcados como [app] <defunct> ocupando IDs de processo. "
     "Causa: O processo pai não chamou a função de sistema wait() ou waitpid() para colher o código de término dos filhos. "
     "Solução técnica: Localize o processo pai responsável com ps -ef | grep defunct. "
     "Envie um sinal de término suave para o processo pai com kill -15 <PID_PAI> para que o init herde e expurgue os zumbis."),

    (137, "Erro 'Too many open files' em servidores web de alto tráfego no Ubuntu", "Sistema Operacional",
     "Sintoma: A aplicação recusa novas conexões de rede acusando erro de limite de descritores de arquivo atingido. "
     "Causa: O limite padrão de arquivos abertos (ulimit -n) de 1024 foi atingido pelo processo de servidor. "
     "Solução técnica: Adicione em /etc/security/limits.conf as linhas: * soft nofile 65536 e * hard nofile 65536. "
     "Para serviços systemd, adicione LimitNOFILE=65536 dentro do bloco [Service] do arquivo de unidade."),

    (138, "Erro 'Failed to fetch' no apt por repositório com protocolo HTTPS em instalação mínima", "Gerenciamento de Pacotes",
     "Sintoma: O comando apt update falha em repositórios https acusando método de transporte desconhecido. "
     "Causa: O pacote apt-transport-https e certificados da autoridade não estão instalados em ambientes mínimos ou Docker. "
     "Solução técnica: Execute sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates."),

    (139, "Cursor piscando e tela preta ao tentar inicializar a interface gráfica GDM3", "Sistema Operacional",
     "Sintoma: O sistema conclui o boot mas não carrega a tela de login gráfico do GNOME, ficando em tela preta com cursor. "
     "Causa: Incompatibilidade do servidor de exibição Wayland com placas gráficas híbridas ou drivers legados. "
     "Solução técnica: Abra o terminal tty com Ctrl + Alt + F3, edite /etc/gdm3/custom.conf, descomente a linha "
     "WaylandEnable=false para forçar o uso do Xorg clássico e reinicie o serviço com sudo systemctl restart gdm3."),

    (140, "Como expandir um volume lógico LVM após aumentar o tamanho do disco virtual na máquina virtual", "Armazenamento",
     "Sintoma: O disco rígido virtual foi aumentado no hipervisor mas a partição / continua com o tamanho antigo. "
     "Causa: A tabela de partições e os volumes LVM não reconhecem automaticamente o novo espaço não alocado. "
     "Solução técnica: Execute echo 1 > /sys/class/block/sda/device/rescan para reconhecer a nova capacidade. "
     "Expanda o volume físico com pvresize /dev/sda3, o volume lógico com lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv "
     "e o sistema de arquivos ext4 com resize2fs /dev/ubuntu-vg/ubuntu-lv."),

    (141, "Erro 'Certificate verification failed: The certificate is not yet valid' no terminal", "Segurança",
     "Sintoma: Comandos curl, wget ou git falham ao acessar qualquer endereço HTTPS com erro de certificado inválido no tempo. "
     "Causa: O relógio da máquina está completamente dessincronizado (ex: marcando anos no passado). "
     "Solução técnica: Force a sincronização do relógio do sistema via NTP executando: "
     "sudo timedatectl set-ntp true && sudo systemctl restart systemd-timesyncd. Valide a hora atual com timedatectl."),

    (142, "Fail2ban não bloqueia tentativas de invasão por força bruta no SSH", "Segurança",
     "Sintoma: O log /var/log/auth.log mostra centenas de tentativas incorretas de senha sem banimento de nenhum IP. "
     "Causa: O backend de leitura do log no fail2ban está configurado como arquivo estático enquanto o Ubuntu 24.04 usa journald. "
     "Solução técnica: No arquivo /etc/fail2ban/jail.local, na seção [sshd], adicione backend = systemd e maxretry = 5. "
     "Reinicie o serviço com sudo systemctl restart fail2ban e consulte o status com fail2ban-client status sshd."),

    (143, "Como configurar interface de rede em modo Bridge para máquinas virtuais KVM/QEMU no Netplan", "Conectividade",
     "Sintoma: Máquinas virtuais KVM criadas no Ubuntu ficam isoladas em NAT sem conseguir receber IP direto da rede local. "
     "Causa: Ausência de uma interface de ponte virtual (bridge) ligada à interface física. "
     "Solução técnica: No arquivo YAML do Netplan, declare a seção bridges: br0: interfaces: [eth0] dhcp4: true. "
     "Remova a configuração de IP direto da interface eth0 e aplique com sudo netplan apply."),

    (144, "Serviço Apache falhando com aviso 'Could not reliably determine the server's fully qualified domain name'", "Serviços & Daemons",
     "Sintoma: Ao iniciar o Apache ele emite alerta AH00558 sobre FQDN e não resolve o nome de host local. "
     "Causa: Diretiva ServerName global não definida nos arquivos de configuração do Apache2. "
     "Solução técnica: Crie o arquivo /etc/apache2/conf-available/fqdn.conf contendo a linha ServerName 127.0.0.1. "
     "Habilite a configuração com sudo a2enconf fqdn e recarregue com sudo systemctl reload apache2."),

    (145, "Erro 'Swapfile has holes' ao tentar ativar arquivo de swap com swapon", "Armazenamento",
     "Sintoma: O comando swapon /swapfile falha acusando que o arquivo contém lacunas (holes). "
     "Causa: O arquivo de swap foi criado utilizando fallocate em sistema de arquivos que aloca blocos esparsos (ex: Btrfs ou XFS). "
     "Solução técnica: Remova o arquivo defeituoso e recrie utilizando o utilitário dd com blocos contínuos: "
     "sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress. Defina chmod 600 /swapfile, execute mkswap /swapfile e swapon /swapfile."),

    (146, "Como alterar o limite de memória virtual vm.max_map_count para Elasticsearch e containers", "Sistema Operacional",
     "Sintoma: Containers do Elasticsearch ou SonarQube falham ao iniciar com erro 'max virtual memory areas vm.max_map_count [65530] is too low'. "
     "Causa: O limite padrão de áreas de memória virtual mapeadas pelo kernel do Linux é insuficiente para bancos de busca. "
     "Solução técnica: Altere o parâmetro em tempo de execução com sudo sysctl -w vm.max_map_count=262144. "
     "Para tornar persistente após reinicializações, adicione a linha vm.max_map_count=262144 em /etc/sysctl.conf."),

    (147, "Placa de rede Gigabit operando apenas em 100Mbps no switch corporativo", "Conectividade",
     "Sintoma: Taxa de transferência de arquivos pela rede local limitada a 10MB/s em cabo de rede de alta velocidade. "
     "Causa: Falha de autonegociação da velocidade no par trançado por interferência ou cabo mal crimpado. "
     "Solução técnica: Inspecione a velocidade atual com ethtool eth0. "
     "Force a autonegociação correta executando sudo ethtool -s eth0 speed 1000 duplex full autoneg on e teste o cabo com testador de continuidade."),

    (148, "Scripts em tarefas do Cron falhando silenciosamente por ausência de PATH completo", "Serviços & Daemons",
     "Sintoma: O script executa com sucesso quando rodado manualmente pelo terminal, mas falha quando disparado pelo crontab. "
     "Causa: O ambiente de execução do cron não carrega o PATH do usuário, contendo apenas /usr/bin e /bin por padrão. "
     "Solução técnica: Defina a variável PATH explicitamente na primeira linha do arquivo crontab (crontab -e): "
     "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin. Use sempre caminhos absolutos para binários nos comandos."),

    (149, "Pasta /tmp cheia travando compilações e execução de programas no Linux", "Armazenamento",
     "Sintoma: Erros de compilação ou falha de criação de sockets informando falta de espaço no diretório temporário. "
     "Causa: Acúmulo de arquivos órfãos criados por aplicações que não foram expurgados automaticamente. "
     "Solução técnica: Execute a limpeza segura dos arquivos com mais de 7 dias utilizando o systemd-tmpfiles: "
     "sudo systemd-tmpfiles --clean. Para limpeza manual forçada, execute rm -rf /tmp/* excluindo arquivos antigos."),

    (150, "Como restaurar o backup de um banco de dados PostgreSQL dump .sql no Ubuntu", "Armazenamento",
     "Sintoma: Necessidade de subir base de dados corporativa a partir de arquivo de backup dump gerado por pg_dump. "
     "Causa: Recuperação de desastres ou migração de infraestrutura de banco de dados. "
     "Solução técnica: Crie o banco de dados de destino com sudo -u postgres createdb nome_do_banco. "
     "Restaure o conteúdo executando sudo -u postgres psql -d nome_do_banco -f /caminho/backup.sql."),

    (151, "Erro 'ModuleNotFoundError' ao rodar script Python pelo cron ou como serviço systemd", "Serviços & Daemons",
     "Sintoma: O serviço falha ao iniciar dizendo que determinado módulo Python instalado não existe. "
     "Causa: O script foi invocado pelo interpretador Python global do sistema (/usr/bin/python3) e não pelo virtualenv onde as libs estão. "
     "Solução técnica: No arquivo de unidade do systemd ou linha do cron, aponte diretamente o executável do venv: "
     "ExecStart=/caminho/do/projeto/.venv/bin/python /caminho/do/projeto/main.py."),

    (152, "Como configurar sincronização contínua de arquivos entre servidores Linux com Rsync via SSH", "Armazenamento",
     "Sintoma: Necessidade de espelhar diretório de dados em servidor secundário sem transferir arquivos repetidos. "
     "Causa: Falta de automação de rotinas de cópia diferencial de segurança. "
     "Solução técnica: Utilize o utilitário rsync com compressão e preservação de permissões via SSH: "
     "rsync -avz --delete -e 'ssh -p 22' /var/www/dados/ usuario@servidor-backup:/var/www/dados/."),

    (153, "Erro de memória esgotada 'fork: Cannot allocate memory' ao digitar comandos no terminal", "Sistema Operacional",
     "Sintoma: Qualquer comando simples como ls ou ps falha com erro de alocação de memória no fork. "
     "Causa: O número total de processos/threads em execução atingiu o limite máximo de PIDs do kernel (pid_max). "
     "Solução técnica: Verifique o limite com sysctl kernel.pid_max. "
     "Encerre processos zumbis ou aplicações fora de controle via killall -9 nome_processo e aumente o limite com sysctl -w kernel.pid_max=4194304."),

    (154, "Bloqueio de ataque DDoS por inundação SYN com ativação de SYN Cookies no kernel Linux", "Segurança",
     "Sintoma: Servidor web para de responder novas requisições com logs dmesg acusando 'possible SYN flooding on port 80'. "
     "Causa: Inundação de pacotes SYN de rede esgotando a fila de conexões pendentes do TCP (SYN backlog). "
     "Solução técnica: Habilite a mitigação por cookies criptográficos de SYN executando: "
     "sudo sysctl -w net.ipv4.tcp_syncookies=1. Adicione a linha net.ipv4.tcp_syncookies = 1 em /etc/sysctl.conf para persistir."),

    (155, "Como recuperar partição acidentalmente deletada no Linux com TestDisk", "Armazenamento",
     "Sintoma: O disco aparece sem tabela de partição após comando fdisk incorreto e dados não montam mais. "
     "Causa: Setor de partição MBR/GPT sobrescrito sem destruição dos dados físicos subjacentes. "
     "Solução técnica: Instale o testdisk com sudo apt install testdisk. Execute sudo testdisk, selecione o dispositivo, "
     "escolha o tipo de partição (EFI GPT ou Intel), selecione 'Analyse' > 'Quick Search' e grave a estrutura original encontrada com 'Write'."),

    (156, "Erro 'Job for cups.service failed' ao tentar imprimir no Ubuntu Desktop", "Serviços & Daemons",
     "Sintoma: Nenhuma impressora é detectada e o painel de impressão do GNOME informa que o serviço de impressão não está disponível. "
     "Causa: O daemon CUPS falhou ao carregar arquivo de configuração de impressoras /etc/cups/printers.conf corrompido. "
     "Solução técnica: Pare o serviço, mova o arquivo corrompido com sudo mv /etc/cups/printers.conf /etc/cups/printers.conf.old "
     "e reinicie o serviço com sudo systemctl restart cups."),

    (157, "Teclado desconfigurado trocando caracteres especiais (ex: cedilha Ç e til ~)", "Sistema Operacional",
     "Sintoma: Digitar teclas de acentuação gera caracteres trocados como ponto-e-vírgula no lugar da cedilha. "
     "Causa: O layout do teclado do console ou sessão gráfica está configurado no padrão americano (US) em vez de ABNT2. "
     "Solução técnica: Reconfigure o teclado pelo terminal executando sudo dpkg-reconfigure keyboard-configuration "
     "e selecione 'Generic 105-key PC' e 'Portuguese (Brazil) - Portuguese (Brazil, with dead keys)'. Ou use localectl set-x11-keymap br abnt2."),

    (158, "Como desativar suspensão e hibernação no Ubuntu Server para evitar travamentos de rede", "Sistema Operacional",
     "Sintoma: O servidor perde conectividade de rede após algumas horas de inatividade sem resposta a ping. "
     "Causa: O sistema operacional entra em modo de economia de energia e suspende os adaptadores de rede. "
     "Solução técnica: Mascare os alvos de suspensão do systemd para desativar permanentemente com: "
     "sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target."),

    (159, "Erro 'Client sent an HTTP request to an HTTPS server' em requisições de API", "Conectividade",
     "Sintoma: A chamada HTTP retorna código de status 400 Bad Request com corpo informando incompatibilidade de protocolo. "
     "Causa: A requisição foi disparada utilizando o prefixo http:// contra uma porta configurada com certificado SSL/TLS (porta 443). "
     "Solução técnica: Corrija a URL da requisição garantindo o esquema https:// ou configure no servidor web (Nginx) "
     "o redirecionamento automático de HTTP para HTTPS na porta 80: return 301 https://$host$request_uri;."),

    (160, "Como monitorar tráfego de rede em tempo real por processo com Nethogs", "Conectividade",
     "Sintoma: Conexão de internet corporativa saturada sem clareza de qual processo está consumindo a banda. "
     "Causa: Falta de visibilidade de consumo de rede por processo em ferramentas genéricas como iftop. "
     "Solução técnica: Instale o Nethogs com sudo apt install nethogs. "
     "Execute com sudo nethogs eth0 para exibir uma tabela dinâmica em tempo real listando cada PID, usuário e taxa de download/upload."),

    (161, "Erro 'sub-process /usr/bin/dpkg returned an error code (2)' ao desinstalar pacote", "Gerenciamento de Pacotes",
     "Sintoma: A desinstalação de um pacote trava com erro no script de remoção do dpkg. "
     "Causa: Scripts de gatilho prerm ou postrm do pacote com comandos quebrados ou caminhos inexistentes. "
     "Solução técnica: Acesse o diretório de metadados com cd /var/lib/dpkg/info/. "
     "Localize os arquivos do pacote com problema (ex: pacote.prerm e pacote.postrm) e renomeie-os. Conclua com sudo dpkg --remove --force-all pacote."),

    (162, "Configuração de IP virtual flutuante de alta disponibilidade com Keepalived no Ubuntu", "Conectividade",
     "Sintoma: Necessidade de redundância de gateway ou proxy reverso onde o IP de atendimento migra automaticamente se um nó cair. "
     "Causa: Falta de configuração de protocolo VRRP (Virtual Router Redundancy Protocol). "
     "Solução técnica: Instale o keepalived com sudo apt install keepalived. Configure /etc/keepalived/keepalived.conf "
     "com vrrp_instance definindo estado MASTER no nó principal e BACKUP no nó secundário com virtual_ipaddress compartilhado."),

    (163, "Tela congelada ao alternar entre monitores externos no Ubuntu com Wayland", "Sistema Operacional",
     "Sintoma: Conectar um segundo monitor via HDMI ou DisplayPort congela a interface gráfica do sistema. "
     "Causa: Divergência na taxa de atualização (refresh rate) entre telas de resoluções diferentes no compositor Wayland. "
     "Solução técnica: Acesse Configurações > Telas e garanta que ambos os monitores estejam na mesma taxa de atualização (ex: 60Hz). "
     "Se o problema persistir, alterne para a sessão Xorg na engrenagem da tela de login."),

    (164, "Configuração de backup incremental com deduplicação nativa utilizando BorgBackup", "Armazenamento",
     "Sintoma: Backups diários consumindo gigabytes repetidos de espaço em disco no servidor. "
     "Causa: Ferramentas de cópia simples que não aplicam algoritmos de deduplicação em nível de bloco. "
     "Solução técnica: Instale o borgbackup com sudo apt install borgbackup. Inicialize o repositório com borg init --encryption=repokey /backup. "
     "Crie rotinas diárias com: borg create --stats --compression lz4 /backup::dia-{now} /var/www /etc."),

    (165, "Erro 'Repository is not signed' ao adicionar repositórios no Ubuntu 24.04 LTS", "Gerenciamento de Pacotes",
     "Sintoma: O comando apt update recusa repositório informando que ele não possui arquivo de liberação assinado. "
     "Causa: Nova exigência do formato deb822 no Ubuntu 24.04 requerendo chaveiro explícito no arquivo /etc/apt/sources.list.d/. "
     "Solução técnica: Baixe a chave GPG em /etc/apt/keyrings/ e crie o arquivo .sources contendo: "
     "Types: deb, URIs: https://..., Suites: jammy, Components: main, Signed-By: /etc/apt/keyrings/chave.gpg."),

    (166, "Como auditar comandos executados por usuários root no Ubuntu com Auditd", "Segurança",
     "Sintoma: Exigência de conformidade de segurança para registrar histórico de comandos e acessos privilegiados de administradores. "
     "Causa: O histórico simples do bash (.bash_history) pode ser apagado ou editado pelo próprio usuário root. "
     "Solução técnica: Instale o auditd com sudo apt install auditd. Adicione regras em /etc/audit/rules.d/audit.rules: "
     "-a always,exit -F arch=b64 -S execve -F euid=0 -k root_actions e consulte os registros com ausearch -k root_actions."),

    (167, "Erro 'Cannot open display' ao rodar aplicativo gráfico via SSH com X11 Forwarding", "Conectividade",
     "Sintoma: Ao tentar abrir um aplicativo gráfico no servidor remoto pelo SSH o terminal retorna 'Error: Can't open display'. "
     "Causa: O pacote xauth não está instalado no servidor ou o X11Forwarding está desabilitado no sshd_config. "
     "Solução técnica: No servidor, instale o xauth com sudo apt install xauth e garanta X11Forwarding yes em /etc/ssh/sshd_config. "
     "No cliente, conecte passando o parâmetro -X: ssh -X usuario@servidor."),

    (168, "Servidor DNS local BIND9 não responde consultas de máquinas clientes da LAN", "Conectividade",
     "Sintoma: O servidor responde a consultas locais via dig @localhost mas máquinas clientes recebem 'Connection refused'. "
     "Causa: A diretiva allow-query no arquivo de configuração do BIND permite apenas localhost por padrão de segurança. "
     "Solução técnica: Edite /etc/bind/named.conf.options e inclua a faixa da rede local: "
     "allow-query { localhost; 192.168.0.0/24; }; e allow-recursion { localhost; 192.168.0.0/24; };. Reinicie com systemctl restart named."),

    (169, "Erro 'No protocol specified' ao rodar aplicativo gráfico como root dentro da sessão de usuário", "Sistema Operacional",
     "Sintoma: Executar sudo gedit ou software gráfico com sudo acusa erro de protocolo de exibição do servidor X. "
     "Causa: Por padrão o servidor Xorg restringe acesso ao display apenas para o usuário proprietário da sessão de desktop. "
     "Solução técnica: Na sessão do usuário comum, libere o acesso ao display para o usuário local root com: "
     "xhost +si:localuser:root antes de invocar o comando administrativo."),

    (170, "Como inspecionar a saúde de discos rígidos e SSDs com o comando smartctl", "Armazenamento",
     "Sintoma: Suspeita de falha iminente de armazenamento com pequenos congelamentos de I/O no Linux. "
     "Causa: Desgaste físico de cabeçote ou setores defeituosos no disco magnético/flash. "
     "Solução técnica: Instale o smartmontools com sudo apt install smartmontools. "
     "Execute sudo smartctl -H /dev/sda para verificar o status de saúde geral e sudo smartctl -A /dev/sda para analisar o atributo Reallocated_Sector_Ct."),

    (171, "Erro 'Address already in use' ao tentar iniciar o servidor Apache na porta 80", "Serviços & Daemons",
     "Sintoma: O Apache2 falha ao iniciar com mensagem 'Address already in use: make_sock: could not bind to address 0.0.0.0:80'. "
     "Causa: Outro servidor web (como Nginx ou lighttpd) já está em execução ocupando a porta TCP 80. "
     "Solução técnica: Descubra o PID do processo concorrente executando sudo fuser -v 80/tcp ou sudo ss -lptn 'sport = :80'. "
     "Desative o serviço conflitante com sudo systemctl stop nginx && sudo systemctl disable nginx."),

    (172, "Como limitar consumo máximo de memória e CPU para serviços com Systemd Cgroups", "Serviços & Daemons",
     "Sintoma: Um serviço secundário entra em vazamento de memória e derruba outros daemons essenciais do servidor. "
     "Causa: Ausência de restrições de isolamento de recursos nos grupos de controle (cgroups) da unidade. "
     "Solução técnica: Abra o arquivo de unidade /etc/systemd/system/meu_servico.service e adicione no bloco [Service]: "
     "CPUQuota=50% e MemoryMax=2G. Aplique imediatamente com sudo systemctl daemon-reload && sudo systemctl restart meu_servico."),

    (173, "Erro 'Operation not permitted' mesmo executando comandos como root dentro de container Docker", "Segurança",
     "Sintoma: Comandos de rede como iptables ou montagem de volumes falham dentro do container Docker com permissão negada. "
     "Causa: Os contêineres Docker rodam por padrão sem capacidades de kernel avançadas (Linux Capabilities) por segurança. "
     "Solução técnica: Inicie o container fornecendo a capacidade pontual necessária com a flag --cap-add=NET_ADMIN "
     "ou --cap-add=SYS_ADMIN em vez de conceder privilégio total."),

    (174, "Como configurar túnel reverso SSH para acessar servidor atrás de NAT sem IP público", "Conectividade",
     "Sintoma: Necessidade de acessar terminal de máquina remota instalada em cliente que não possui IP fixo ou portas abertas. "
     "Causa: Firewall de borda e NAT do provedor de internet bloqueando conexões de entrada. "
     "Solução técnica: Na máquina do cliente, execute um túnel reverso apontando para um servidor intermediário com IP público: "
     "ssh -R 2222:localhost:22 usuario@servidor_publico -N. Acesse a máquina no servidor público com ssh -p 2222 localhost."),

    (175, "Erro 'Signature by key uses weak algorithm (rsa1024)' ao atualizar pacotes no apt", "Gerenciamento de Pacotes",
     "Sintoma: O comando apt update acusa aviso ou erro de assinatura fraca rejeitando chaves criptográficas de 1024 bits. "
     "Causa: As distribuições modernas do Ubuntu deprecam chaves RSA menores que 2048 bits por motivos de segurança criptográfica. "
     "Solução técnica: Contate o mantenedor do repositório para obter a chave RSA 4096 moderna ou migre para repositório oficial equivalente."),

    (176, "Como forçar o kernel Linux a liberar memória de Buffers e PageCache", "Sistema Operacional",
     "Sintoma: A memória livre indicada no comando free -m parece quase zerada devido à retenção de caches de leitura de disco. "
     "Causa: O kernel Linux utiliza a RAM ociosa para cache de páginas até que uma aplicação exija mais memória física. "
     "Solução técnica: Para forçar a liberação imediata antes de testes de benchmarking, execute: "
     "sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches."),

    (177, "Máquina Windows na mesma rede local não responde a comandos ping do Linux", "Conectividade",
     "Sintoma: O comando ping 192.168.1.150 retorna 100% de perda de pacotes, embora a máquina esteja ligada e navegando. "
     "Causa: O Firewall do Windows bloqueia solicitações de eco ICMPv4 de entrada por padrão na rede privada/pública. "
     "Solução técnica: No computador com Windows de destino, abra o PowerShell como Administrador e habilite o ping: "
     "netsh advfirewall firewall add rule name=\"Permitir Ping ICMPv4\" protocol=icmpv4:8,any dir=in action=allow."),

    (178, "Como configurar agregação de placas de rede (Bonding / LACP) no Ubuntu Server", "Conectividade",
     "Sintoma: Necessidade de tolerância a falhas de cabos e aumento de largura de banda combinando duas portas Ethernet físicas. "
     "Causa: Interfaces separadas sem protocolo de agregação de links (IEEE 802.3ad). "
     "Solução técnica: Configure o arquivo Netplan com uma interface bond: "
     "bonds: bond0: interfaces: [eth0, eth1] parameters: mode: 802.3ad mii-monitor-interval: 100 dhcp4: true e execute netplan apply."),

    (179, "Erro 'Cannot allocate memory' no Redis ao tentar salvar dados com BGSAVE", "Serviços & Daemons",
     "Sintoma: O banco em memória Redis não consegue persistir o arquivo RDB em disco emitindo erro de fork de memória. "
     "Causa: O kernel Linux está com a política de overcommit restrita impedindo o processo filho de duplicar o mapa de memória. "
     "Solução técnica: Habilite o overcommit de memória executando sudo sysctl vm.overcommit_memory=1 "
     "e adicione a linha vm.overcommit_memory = 1 no arquivo /etc/sysctl.conf para persistir."),

    (180, "Como monitorar integridade de arquivos críticos do sistema contra adulteração com AIDE", "Segurança",
     "Sintoma: Necessidade de auditoria contra invasões que possam ter modificado binários em /bin, /sbin ou /etc. "
     "Causa: Falta de verificação de integridade de hash de arquivos de sistema (File Integrity Monitoring). "
     "Solução técnica: Instale o AIDE com sudo apt install aide. Inicialize o banco de hashes com sudo aideinit. "
     "Copie a base com sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db e execute auditorias com sudo aide --check."),

    (181, "Erro 'Permission denied (publickey)' ao clonar repositório Git corporativo via SSH", "Segurança",
     "Sintoma: O comando git clone git@gitlab.empresa.local:... falha imediatamente com permissão negada por chave pública. "
     "Causa: A chave privada SSH não foi carregada no agente de autenticação da sessão ativa. "
     "Solução técnica: Inicie o ssh-agent com eval $(ssh-agent -s) e adicione a chave privada com ssh-add ~/.ssh/id_ed25519. "
     "Verifique com ssh-add -l se a chave consta carregada na memória."),

    (182, "Configuração de proxy reverso Nginx com certificado SSL gratuito Let's Encrypt (Certbot)", "Serviços & Daemons",
     "Sintoma: Necessidade de publicar aplicação HTTP local na internet de forma segura com criptografia HTTPS automática. "
     "Causa: Ausência de certificado digital SSL assinado e homologado por navegadores. "
     "Solução técnica: Instale o Certbot com sudo apt install certbot python3-certbot-nginx. "
     "Gere e configure os certificados automaticamente no Nginx executando: sudo certbot --nginx -d meu-site.empresa.com.br."),

    (183, "Erro 'Cannot create directory /home/usuario: Permission denied' ao criar novos usuários", "Sistema Operacional",
     "Sintoma: O comando useradd -m falha ao tentar criar o diretório de perfil pessoal do usuário. "
     "Causa: As permissões do diretório pai /home foram alteradas inadvertidamente retirando direito de escrita do root. "
     "Solução técnica: Restaure as permissões corretas de sistema com sudo chown root:root /home e sudo chmod 755 /home. "
     "Em seguida crie o usuário normalmente com sudo useradd -m -s /bin/bash novo_usuario."),

    (184, "Como configurar cotas de disco por usuário no sistema de arquivos ext4", "Armazenamento",
     "Sintoma: Usuários compartilhando servidores de arquivos enchem a partição de dados sem nenhum limite de consumo. "
     "Causa: Ausência de cotas ativadas no ponto de montagem do sistema de arquivos. "
     "Solução técnica: No arquivo /etc/fstab, adicione a opção usrquota nas opções de montagem da partição. "
     "Remonte a partição, inicialize os arquivos de cota com sudo quotacheck -cugm /dados e defina o limite do usuário com sudo edquota -u usuario."),

    (185, "Kernel Panic após upgrade de driver de terceiros (Fatal exception in interrupt)", "Sistema Operacional",
     "Sintoma: O computador não inicializa após atualização de driver e exibe mensagem de pânico de kernel no console. "
     "Causa: Módulo DKMS de terceiro incompatível com a versão mais recente do kernel Linux instalada. "
     "Solução técnica: Reinicie e selecione o kernel estável anterior no menu GRUB. "
     "Após o boot com sucesso, identifique o módulo defeituoso com dkms status e remova-o com sudo dkms remove modulo/versao --all."),

    (186, "Como alterar a MTU no Netplan para resolver fragmentação de pacotes em túneis GRE/VPN", "Conectividade",
     "Sintoma: Conexões através de túneis corporativos perdem pacotes e páginas grandes não carregam completamente. "
     "Causa: O cabeçalho adicional do encapsulamento da VPN excede o tamanho máximo de quadro padrão de 1500 bytes. "
     "Solução técnica: No arquivo de configuração do Netplan (/etc/netplan/*.yaml), adicione a diretiva mtu: 1420 "
     "dentro da seção da interface de rede correspondente e aplique com sudo netplan apply."),

    (187, "Erro 'System has not been booted with systemd as init system' dentro de container Docker", "Serviços & Daemons",
     "Sintoma: Ao tentar rodar systemctl start nginx dentro de um container Docker padrão ele falha com erro de init system. "
     "Causa: Imagens Docker comuns não executam o systemd como PID 1 para economizar recursos e manter isolamento. "
     "Solução técnica: Inicie o serviço diretamente pelo script de serviço com service nginx start ou invoque o binário "
     "diretamente no ENTRYPOINT do container: nginx -g 'daemon off;'."),

    (188, "Como configurar encaminhamento de pacotes IPv4 (IP Forwarding) para roteador Linux", "Conectividade",
     "Sintoma: O servidor possui duas placas de rede mas não repassa pacotes entre a rede interna e a internet. "
     "Causa: O recurso de encaminhamento de pacotes do kernel Linux (IP Forwarding) está desativado por padrão de segurança. "
     "Solução técnica: Habilite em tempo de execução com sudo sysctl -w net.ipv4.ip_forward=1. "
     "Descomente a linha net.ipv4.ip_forward=1 em /etc/sysctl.conf para manter persistente e configure regras de NAT no iptables."),

    (189, "Erro 'GnuTLS recv error (-110)' ao clonar repositórios Git pesados", "Conectividade",
     "Sintoma: O clone de repositórios grandes trava em 80% do download dos objetos com erro de conexão encerrada. "
     "Causa: Timeout de buffer HTTP no transporte do Git em conexões com alta latência. "
     "Solução técnica: Aumente o tamanho do buffer de transferência do Git executando: "
     "git config --global http.postBuffer 524288000 e clone inicialmente com profundidade rasa: git clone --depth 1 <URL>."),

    (190, "Como monitorar temperatura de CPU e rotação de ventoinhas no Ubuntu com lm-sensors", "Sistema Operacional",
     "Sintoma: Servidor desligando sozinho repentinamente durante picos de processamento em dias quentes. "
     "Causa: Superaquecimento da CPU atingindo o limite térmico (Thermal Throttling / Critical Temperature). "
     "Solução técnica: Instale o lm-sensors com sudo apt install lm-sensors. Execute sudo sensors-detect respondendo 'YES' às perguntas. "
     "Monitore as temperaturas em tempo real com o comando sensors ou watch -n 1 sensors."),

    (191, "Sessão SSH desconecta frequentemente após alguns minutos de inatividade (Broken pipe)", "Conectividade",
     "Sintoma: O terminal remoto congela e desconecta exibindo 'client_loop: send disconnect: Broken pipe'. "
     "Causa: Roteadores ou firewalls intermediários descartam estados de conexão TCP sem tráfego ativo após timeout. "
     "Solução técnica: No cliente SSH, adicione em ~/.ssh/config: Host * ServerAliveInterval 60 ServerAliveCountMax 3. "
     "Isso enviará pacotes de sinal de vida nulos a cada 60 segundos mantendo o túnel aberto."),

    (192, "Como configurar espelhamento de tráfego de rede (Port Mirroring) com Tc no Linux", "Conectividade",
     "Sintoma: Necessidade de enviar cópia de todos os pacotes de uma interface para servidor de análise de segurança (IDS/Snort). "
     "Causa: Ausência de switch gerenciável para espelhamento físico de portas. "
     "Solução técnica: Utilize o subsistema Traffic Control (tc) do Linux: "
     "sudo tc qdisc add dev eth0 ingress e sudo tc filter add dev eth0 parent ffff: protocol all u32 match u32 0 0 action mirred egress mirror dev eth1."),

    (193, "Erro no apt avisando que o repositório não possui arquivo Release (Release file is missing)", "Gerenciamento de Pacotes",
     "Sintoma: O comando apt update falha em servidores legados com versões antigas do Ubuntu (ex: 18.04 ou 20.10). "
     "Causa: A versão da distribuição atingiu o status de End of Life (EOL) e os pacotes foram movidos para os servidores de arquivo histórico. "
     "Solução técnica: Edite /etc/apt/sources.list e substitua as ocorrências de archive.ubuntu.com por old-releases.ubuntu.com."),

    (194, "Como configurar autenticação centralizada de usuários Linux no Active Directory corporativo com SSSD", "Autenticação",
     "Sintoma: Necessidade de permitir que colaboradores façam login no Ubuntu utilizando as mesmas credenciais do domínio Windows. "
     "Causa: Gerenciamento manual e descentralizado de senhas locais em cada máquina Linux. "
     "Solução técnica: Instale o SSSD com sudo apt install sssd realmd adcli. "
     "Junte a máquina ao domínio com sudo realm join --user=administrador empresa.local e configure a criação automática de /home no PAM."),

    (195, "Erro 'Disk /dev/sda contains a GPT signatures, but write failed' ao formatar disco", "Armazenamento",
     "Sintoma: Utilitários de particionamento falham ao tentar gravar nova tabela de partição MBR em disco reutilizado. "
     "Causa: Assinaturas de tabela GPT residuais gravadas no final do disco causando conflito estrutural. "
     "Solução técnica: Limpe completamente todas as assinaturas antigas executando: "
     "sudo wipefs -a /dev/sda ou utilize sudo sgdisk --zap-all /dev/sda antes de criar a nova partição."),

    (196, "Como configurar failover rápido de servidores DNS no resolv.conf do Linux", "Conectividade",
     "Sintoma: Quando o DNS primário cai a navegação web fica travando por 10 segundos antes de tentar o secundário. "
     "Causa: O tempo limite padrão de consulta do resolvedor do Linux é muito elevado (5 segundos por tentativa). "
     "Solução técnica: Adicione diretivas otimizadas no arquivo /etc/resolv.conf: "
     "options timeout:1 attempts:2 rotate. Isso forçará a tentativa no DNS secundário em apenas 1 segundo."),

    (197, "Erro 'su: Authentication failure' ao tentar alternar para usuário root no Ubuntu recém-instalado", "Segurança",
     "Sintoma: O administrador digita su - e recebe falha de autenticação mesmo digitando a senha correta de seu usuário. "
     "Causa: A conta de root vem bloqueada sem senha definida por padrão no Ubuntu, sendo obrigatório o uso do sudo. "
     "Solução técnica: Utilize o comando sudo -i ou sudo su - informando a senha de seu próprio usuário com privilégio de admin. "
     "Para definir uma senha para o root se estritamente necessário, execute sudo passwd root."),

    (198, "Como desativar suporte ao protocolo IPv6 no Ubuntu temporariamente ou permanentemente", "Conectividade",
     "Sintoma: Lentidão em consultas DNS e conexões de rede em ambientes corporativos que não suportam roteamento IPv6. "
     "Causa: O sistema tenta conexão preferencial por IPv6 e aguarda timeout antes de recorrer ao IPv4. "
     "Solução técnica: Adicione em /etc/sysctl.conf as linhas: net.ipv6.conf.all.disable_ipv6 = 1 e net.ipv6.conf.default.disable_ipv6 = 1. "
     "Aplique imediatamente sem reiniciar com sudo sysctl -p."),

    (199, "Erro 'No space left on device' durante compilação com GCC usando arquivos em /dev/shm", "Armazenamento",
     "Sintoma: Compilações de software em C/C++ ou instâncias de bancos de dados em memória abortam por falta de espaço no /dev/shm. "
     "Causa: O sistema de arquivos de memória compartilhada /dev/shm (tmpfs) atingiu o limite padrão de 50% da RAM física. "
     "Solução técnica: Remonte o volume temporário com tamanho expandido executando: "
     "sudo mount -o remount,size=8G /dev/shm."),

    (200, "Como restaurar o arquivo de senhas /etc/passwd corrompido ou acidentalmente apagado", "Sistema Operacional",
     "Sintoma: Nenhum login funciona e o terminal não reconhece usuários com erro 'whoami: cannot find name for user ID'. "
     "Causa: Edição manual com falha ou exclusão acidental do arquivo fundamental de contas /etc/passwd. "
     "Solução técnica: O sistema operacional mantém cópias de segurança automáticas. Inicialize em Modo de Recuperação e restaure com: "
     "sudo cp /etc/passwd- /etc/passwd && sudo chmod 644 /etc/passwd && sudo chown root:root /etc/passwd.")
]

# Construção dos dicionários finais
microsoft_docs = []
for tid, title, cat, content in ms_docs_raw:
    microsoft_docs.append({
        "id": tid,
        "titulo": title,
        "fonte": "Microsoft",
        "categoria": cat,
        "conteudo": content,
        "metadados": {
            "versao": "Windows 10/11 / Windows Server",
            "autor": "Suporte Corporativo Microsoft",
            "tags": [cat.lower(), "windows", "microsoft", "helpdesk"],
            "doc_id": tid
        }
    })

ubuntu_docs = []
for tid, title, cat, content in ub_docs_raw:
    ubuntu_docs.append({
        "id": tid,
        "titulo": title,
        "fonte": "Ubuntu",
        "categoria": cat,
        "conteudo": content,
        "metadados": {
            "versao": "Ubuntu 22.04/24.04 LTS",
            "autor": "Suporte Técnico Linux / DevOps",
            "tags": [cat.lower(), "ubuntu", "linux", "sysadmin"],
            "doc_id": tid
        }
    })

with open("data/raw/microsoft_faq.json", "w", encoding="utf-8") as f:
    json.dump(microsoft_docs, f, indent=2, ensure_ascii=False)

with open("data/raw/ubuntu_logs.json", "w", encoding="utf-8") as f:
    json.dump(ubuntu_docs, f, indent=2, ensure_ascii=False)

print(f"Salvos com sucesso: {len(microsoft_docs)} documentos Microsoft e {len(ubuntu_docs)} documentos Ubuntu (TOTAL: 200 DOCUMENTOS ÚNICOS).")

# =====================================================================
# MATRIZ DE PADRÃO-OURO (GROUND TRUTH) - 60 CONSULTAS ROTULADAS
# =====================================================================
queries_data = [
    # Cenário A: Microsoft (Consultas 1 a 30)
    {"query_id": 1, "cenario": "Microsoft", "texto": "minha internet nao funciona e aparece rede nao identificada", "categoria": "Conectividade", "doc_relevante": 1},
    {"query_id": 2, "cenario": "Microsoft", "texto": "como conectar na vpn da empresa no windows", "categoria": "Conectividade", "doc_relevante": 2},
    {"query_id": 3, "cenario": "Microsoft", "texto": "o wifi esta muito lento e caindo toda hora", "categoria": "Conectividade", "doc_relevante": 3},
    {"query_id": 4, "cenario": "Microsoft", "texto": "nao consigo acessar a pasta compartilhada no servidor", "categoria": "Conectividade", "doc_relevante": 4},
    {"query_id": 5, "cenario": "Microsoft", "texto": "problema para resolver nomes dns internos", "categoria": "Conectividade", "doc_relevante": 5},
    {"query_id": 6, "cenario": "Microsoft", "texto": "nao consigo conectar na area de trabalho remota rdp", "categoria": "Conectividade", "doc_relevante": 6},
    {"query_id": 7, "cenario": "Microsoft", "texto": "aviso de conflito de endereco ip no computador", "categoria": "Conectividade", "doc_relevante": 7},
    {"query_id": 8, "cenario": "Microsoft", "texto": "sites internos travando e conexao fragmentando pacotes", "categoria": "Conectividade", "doc_relevante": 8},
    {"query_id": 9, "cenario": "Microsoft", "texto": "chamada do microsoft teams com audio falhando e cortando", "categoria": "Conectividade", "doc_relevante": 9},
    {"query_id": 10, "cenario": "Microsoft", "texto": "minha placa de rede ethernet desliga sozinha quando paro de usar", "categoria": "Conectividade", "doc_relevante": 10},

    {"query_id": 11, "cenario": "Microsoft", "texto": "esqueci minha senha e minha conta de usuario foi bloqueada", "categoria": "Autenticação", "doc_relevante": 11},
    {"query_id": 12, "cenario": "Microsoft", "texto": "falha na relacao de confianca entre estacao e dominio", "categoria": "Autenticação", "doc_relevante": 12},
    {"query_id": 13, "cenario": "Microsoft", "texto": "nao recebo notificacao do aplicativo autenticador mfa", "categoria": "Autenticação", "doc_relevante": 13},
    {"query_id": 14, "cenario": "Microsoft", "texto": "relogio do computador com diferenca de horario e erro de login", "categoria": "Autenticação", "doc_relevante": 14},
    {"query_id": 15, "cenario": "Microsoft", "texto": "outlook fica pedindo senha o tempo todo", "categoria": "Autenticação", "doc_relevante": 15},
    {"query_id": 16, "cenario": "Microsoft", "texto": "como forcar atualizacao das politicas de gpo", "categoria": "Autenticação", "doc_relevante": 16},
    {"query_id": 17, "cenario": "Microsoft", "texto": "pin do windows hello nao disponivel apos ligar", "categoria": "Autenticação", "doc_relevante": 17},
    {"query_id": 18, "cenario": "Microsoft", "texto": "leitor de cartao inteligente smart card nao reconhecido", "categoria": "Autenticação", "doc_relevante": 18},
    {"query_id": 19, "cenario": "Microsoft", "texto": "auditoria de tentativas de senha incorreta no windows", "categoria": "Autenticação", "doc_relevante": 19},
    {"query_id": 20, "cenario": "Microsoft", "texto": "alterei a senha no computador mas na nuvem nao atualizou", "categoria": "Autenticação", "doc_relevante": 20},

    {"query_id": 21, "cenario": "Microsoft", "texto": "computador travou e deu tela azul critical process died", "categoria": "Sistema Operacional", "doc_relevante": 21},
    {"query_id": 22, "cenario": "Microsoft", "texto": "meu computador ta muito lento com disco em 100 porcento", "categoria": "Sistema Operacional", "doc_relevante": 22},
    {"query_id": 23, "cenario": "Microsoft", "texto": "windows update travado baixando atualizacoes", "categoria": "Sistema Operacional", "doc_relevante": 23},
    {"query_id": 24, "cenario": "Microsoft", "texto": "windows travado na tela azul de reparo automatico", "categoria": "Sistema Operacional", "doc_relevante": 24},
    {"query_id": 25, "cenario": "Microsoft", "texto": "como voltar o windows para uma data anterior restaurar", "categoria": "Sistema Operacional", "doc_relevante": 25},
    {"query_id": 26, "cenario": "Microsoft", "texto": "processo interrupcoes do sistema usando muita cpu", "categoria": "Sistema Operacional", "doc_relevante": 26},
    {"query_id": 27, "cenario": "Microsoft", "texto": "erro de boot winload.efi ausente no windows", "categoria": "Sistema Operacional", "doc_relevante": 27},
    {"query_id": 28, "cenario": "Microsoft", "texto": "como fazer inicializacao limpa para testar programas", "categoria": "Sistema Operacional", "doc_relevante": 28},
    {"query_id": 29, "cenario": "Microsoft", "texto": "adicionar caminho no path do sistema windows", "categoria": "Sistema Operacional", "doc_relevante": 29},
    {"query_id": 30, "cenario": "Microsoft", "texto": "barra de tarefas travou e menu iniciar nao clica", "categoria": "Sistema Operacional", "doc_relevante": 30},

    # Cenário B: Ubuntu (Consultas 31 a 60)
    {"query_id": 31, "cenario": "Ubuntu", "texto": "erro could not get lock dpkg quebrado no terminal", "categoria": "Gerenciamento de Pacotes", "doc_relevante": 101},
    {"query_id": 32, "cenario": "Ubuntu", "texto": "como configurar ip fixo com netplan no ubuntu", "categoria": "Conectividade", "doc_relevante": 102},
    {"query_id": 33, "cenario": "Ubuntu", "texto": "computador liga na tela grub rescue nao inicia o linux", "categoria": "Sistema Operacional", "doc_relevante": 103},
    {"query_id": 34, "cenario": "Ubuntu", "texto": "servidor linux travando com processo usando toda a memoria e cpu", "categoria": "Sistema Operacional", "doc_relevante": 104},
    {"query_id": 35, "cenario": "Ubuntu", "texto": "nao consigo conectar por ssh na porta 22 connection refused", "categoria": "Conectividade", "doc_relevante": 105},
    {"query_id": 36, "cenario": "Ubuntu", "texto": "disco cheio no ubuntu como liberar espaco em var log", "categoria": "Armazenamento", "doc_relevante": 106},
    {"query_id": 37, "cenario": "Ubuntu", "texto": "como montar hd ou particao automaticamente no fstab", "categoria": "Armazenamento", "doc_relevante": 107},
    {"query_id": 38, "cenario": "Ubuntu", "texto": "permissao negada em pasta chmod chown para usuario", "categoria": "Segurança", "doc_relevante": 108},
    {"query_id": 39, "cenario": "Ubuntu", "texto": "como ativar firewall ufw e liberar portas no ubuntu", "categoria": "Segurança", "doc_relevante": 109},
    {"query_id": 40, "cenario": "Ubuntu", "texto": "wifi nao aparece no notebook com ubuntu driver broadcom", "categoria": "Conectividade", "doc_relevante": 110},

    {"query_id": 41, "cenario": "Ubuntu", "texto": "como reiniciar servico e ver logs com systemctl e journalctl", "categoria": "Serviços & Daemons", "doc_relevante": 111},
    {"query_id": 42, "cenario": "Ubuntu", "texto": "como colocar script para rodar sozinho todo dia no crontab", "categoria": "Serviços & Daemons", "doc_relevante": 112},
    {"query_id": 43, "cenario": "Ubuntu", "texto": "esqueci a senha de root e administrador no ubuntu como recuperar", "categoria": "Segurança", "doc_relevante": 113},
    {"query_id": 44, "cenario": "Ubuntu", "texto": "servidor matando processos por falta de memoria como criar swap", "categoria": "Armazenamento", "doc_relevante": 114},
    {"query_id": 45, "cenario": "Ubuntu", "texto": "tela preta com placa de video nvidia no linux", "categoria": "Sistema Operacional", "doc_relevante": 115},
    {"query_id": 46, "cenario": "Ubuntu", "texto": "erro de permissao ao rodar comando docker sem sudo", "categoria": "Serviços & Daemons", "doc_relevante": 116},
    {"query_id": 47, "cenario": "Ubuntu", "texto": "kernel panic unable to mount root fs apos atualizar o ubuntu", "categoria": "Sistema Operacional", "doc_relevante": 117},
    {"query_id": 48, "cenario": "Ubuntu", "texto": "como mudar o horario e fuso horario no linux timedatectl", "categoria": "Sistema Operacional", "doc_relevante": 118},
    {"query_id": 49, "cenario": "Ubuntu", "texto": "como ver qual processo esta lendo e escrevendo muito no disco", "categoria": "Armazenamento", "doc_relevante": 119},
    {"query_id": 50, "cenario": "Ubuntu", "texto": "como fazer login por chave ssh sem precisar digitar senha", "categoria": "Segurança", "doc_relevante": 120},

    {"query_id": 51, "cenario": "Ubuntu", "texto": "erro de chave gpg expirada ao dar apt update", "categoria": "Gerenciamento de Pacotes", "doc_relevante": 121},
    {"query_id": 52, "cenario": "Ubuntu", "texto": "servidor nao pinga fora da rede rota padrao sumiu", "categoria": "Conectividade", "doc_relevante": 122},
    {"query_id": 53, "cenario": "Ubuntu", "texto": "erro no initramfs prompt apos desligar no botao", "categoria": "Sistema Operacional", "doc_relevante": 123},
    {"query_id": 54, "cenario": "Ubuntu", "texto": "particao montou como somente leitura read only reparar com fsck", "categoria": "Armazenamento", "doc_relevante": 124},
    {"query_id": 55, "cenario": "Ubuntu", "texto": "como ver quais portas e programas estao ouvindo com comando ss", "categoria": "Segurança", "doc_relevante": 125},
    {"query_id": 56, "cenario": "Ubuntu", "texto": "configurar servico no systemd para reiniciar sozinho se cair", "categoria": "Serviços & Daemons", "doc_relevante": 126},
    {"query_id": 57, "cenario": "Ubuntu", "texto": "disco 100 porcento ocupado mas du nao acha arquivos apagados abertos", "categoria": "Armazenamento", "doc_relevante": 127},
    {"query_id": 58, "cenario": "Ubuntu", "texto": "erro no space left on device mesmo com espaco livre inodes", "categoria": "Armazenamento", "doc_relevante": 128},
    {"query_id": 59, "cenario": "Ubuntu", "texto": "erro etc sudoers is world writable perdi acesso ao sudo", "categoria": "Segurança", "doc_relevante": 129},
    {"query_id": 60, "cenario": "Ubuntu", "texto": "warning remote host identification has changed ssh known hosts", "categoria": "Segurança", "doc_relevante": 130}
]

ground_truth = []
for q in queries_data:
    ground_truth.append({
        "consulta_id": q["query_id"],
        "cenario": q["cenario"],
        "consulta_texto": q["texto"],
        "categoria_esperada": q["categoria"],
        "documento_relevante_id": q["doc_relevante"],
        "relevancia_binaria": 1
    })

with open("data/ground_truth.json", "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, indent=2, ensure_ascii=False)

print(f"Salvo ground_truth.json contendo {len(ground_truth)} consultas rotuladas.")
