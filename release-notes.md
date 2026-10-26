OpenWrt **25.12.6** for **Cudy WR1300 v4**, with LuCI HTTPS, relayd and iwinfo.
Kernel 6.12.112.

Use **`squashfs-sysupgrade.bin`** to upgrade an existing OpenWrt installation.
Back up your settings and upload it through LuCI, or run `sysupgrade -T`
before installing over SSH. The `initramfs` file is for RAM boot, not sysupgrade.

Upgraded my router from 23.05.5 with settings retained. 5 GHz WPA3 client
mode works; other modes and hardware functions still need testing.

[Install instructions](https://github.com/stephenscholz/openwrt-cudy-wr1300-v4#download--install)
· [Build notes](https://github.com/stephenscholz/openwrt-cudy-wr1300-v4/blob/main/docs/BUILDING.md)
