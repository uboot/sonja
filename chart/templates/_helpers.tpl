{{/*
Expand the name of the chart.
*/}}
{{- define "sonja.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "sonja.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sonja.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sonja.labels" -}}
helm.sh/chart: {{ include "sonja.chart" . }}
{{ include "sonja.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sonja.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sonja.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "sonja.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "sonja.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a daemon.json for Docker for Windows
*/}}
{{- define "sonja.daemonJson" -}}
{
    "hosts": ["tcp://0.0.0.0:2375", "npipe://"],
    "insecure-registries": {{ $.Values.insecureRegistries | toJson }},
    "mtu": {{ .Values.mtu | default 1500 }}
}
{{- end }}

{{/*
Create a Base64 encoded daemon.json for Docker for Windows
*/}}
{{- define "sonja.daemonJsonB64" -}}
{{ include "sonja.daemonJson" . | b64enc }}
{{- end }}
