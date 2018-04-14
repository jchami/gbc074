# Projeto 1
Sistema cliente servidor com dois módulos

* 1 Módulo cliente
* 1 thread recebendo comandos
* 1 thread exibindo resultados
* 1 Módulo servidor
* 1 thread recebendo comandos e colocando em uma fila
* 1 thread consumindo da fila e colocando em fila para logar em disco e em outra para processamento
* Comandos são CRUD em mapa <BigInteger, String>
* Chave pode ter 20 bytes
* Valor pode ter até 1400 bytes
* No caso de reinicialização do processo, o log do disco deve ser reexecutado e o estado do mapa recuperado antes de novos comandos serem aceitos.
* Toda comunicação é via UDP. Dois sockets diferentes são usados.
* Todas as portas usadas na comunicação são especificadas via arquivos de configuração.
* Diversos clientes podem ser iniciados em paralelo e contactando o mesmo servidor.