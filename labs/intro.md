# Intro Lab – GNS3 Warm-up

Welcome! In this lab you will:

1. Confirm access to the **GNS3 Web UI** (see the right pane).
2. Create a new project called `intro-lab`.
3. Add a **Cisco router** and a **switch**.
4. Connect them and verify interface link status.

> Tip: Drag the vertical bar between the panes to resize the instructions area.

## Steps

1. Click **New Project** in the GNS3 Web UI.
2. Name it `intro-lab`.
3. Drag a router and switch into the topology.
4. Connect them with a link.
5. Start both nodes and open the console.

### Verify

```text
R1# show ip interface brief
SW1# show interface status
```

If interfaces are up/up, you’re good to go!
