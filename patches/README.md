# WR1300 v4 patch

Based on the patch linked in
[OpenWrt #22082](https://github.com/openwrt/openwrt/issues/22082):

- [Jan Brudna's mailing-list patch](https://patchwork.ozlabs.org/project/openwrt/patch/20260512133722.896830-1-jan.brudna@gmail.com/)
- [zekica's patch snapshot](https://gist.github.com/zekica/26302f4584bec1ae231764aa04b55e2e),
  revision `eb0d541c267f13fe044d49f6c0b7f0d131ed1884`
- [GuoShuangyan's WR1300 v4 build](https://github.com/GuoShuangyan/Openwrt-Cudy-WR1300-v4)

The bundled patch applies to OpenWrt `v25.12.6`. It adds the v4 profile,
device tree and LEDs, and shares the device-tree definitions with v1–v3.

My change: the extra `SUPPORTED_DEVICES` entry for v4 is `R98` instead of
the copied v3 entries `cudy,wr1300 R30`. The native `cudy,wr1300-v4` entry
is added automatically by OpenWrt.

The LED polarity definitions differ from the older firmware and haven't
been checked on the hardware yet. The patch retains its original license
headers; device-tree files are `GPL-2.0-or-later OR MIT`.
