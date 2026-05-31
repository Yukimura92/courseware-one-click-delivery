# 课件一键交付包（GitHub 脱敏版）

这是一个用于公开仓库的 Skill 副本，保留了课件交付包的核心工作流：

1. 生成小红书课件拼图封面。
2. 生成逐字稿和教学设计 Word 文档。
3. 把课件前 6 页贴入课堂屏幕样机图。

## 脱敏说明

本目录已移除：

- 真实本地课件库路径。
- 历史项目编号和真实项目配置。
- 绑定单个项目的专用脚本。
- 个人账号、密钥、Cookie、Token 等敏感信息。

## 脚本说明

```text
agents/stage1_collage.py          生成 2 图、5 图、12 图拼图
agents/stage2_docs.py             根据 JSON 内容生成逐字稿和教学设计
agents/stage3_mockup.py           生成课堂屏幕样机展示图
agents/config.example.json        阶段 1/3 的示例配置
agents/stage2_content.example.json 阶段 2 的示例内容
```

使用前，复制示例配置并替换成本地路径：

```text
agents/config.example.json -> agents/config.local.json
```

`config.local.json` 不建议提交到公开仓库。

## 公开发布前检查

- 确认 `references/样机图/课堂屏幕样机/` 下的图片拥有公开发布或再分发权限。
- 不要提交真实项目配置、真实课件路径、用户资料或平台凭证。
- 如需保留个人工作流版本，请使用原始私有 Skill，不要在公开仓库中继续写入真实项目数据。
