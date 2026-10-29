{{- define "dp.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 50 | trimSuffix "-" -}}
{{- end -}}

{{- define "dp.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "dp.selector" -}}
app.kubernetes.io/name: {{ .root.Chart.Name }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- /* image: dict "root" . "name" "api" */ -}}
{{- define "dp.image" -}}
{{- $r := .root.Values.image -}}
{{- $repo := index $r.repositories .name -}}
{{- $tag := default .root.Chart.AppVersion $r.tag -}}
{{- if $r.registry -}}{{ printf "%s/%s:%s" (trimSuffix "/" $r.registry) $repo $tag }}{{- else -}}{{ printf "%s:%s" $repo $tag }}{{- end -}}
{{- end -}}

{{- define "dp.secretName" -}}
{{- default (printf "%s-secrets" (include "dp.fullname" .)) .Values.secrets.existingSecret -}}
{{- end -}}

{{- define "dp.podSecurity" -}}
securityContext:
  runAsNonRoot: true
  runAsUser: {{ .uid | default 10001 }}
  seccompProfile: {type: RuntimeDefault}
{{- end -}}

{{- define "dp.containerSecurity" -}}
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: {drop: [ALL]}
{{- end -}}

{{- define "dp.pullSecrets" -}}
{{- with .Values.image.pullSecrets }}
imagePullSecrets:
{{- range . }}
  - name: {{ . }}
{{- end }}
{{- end }}
{{- end -}}
