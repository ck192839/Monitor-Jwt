import * as echarts from "echarts";

function formatTime(value, withSeconds = false) {
    const timestamp = typeof value === 'string' && /^\d+$/.test(value) ? Number(value) : value
    const date = new Date(timestamp)
    if(Number.isNaN(date.getTime())) return ''
    return date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: withSeconds ? '2-digit' : undefined
    })
}

function defaultOption(name, dataX, config = {}) {
    const styles = getComputedStyle(document.documentElement)
    const textColor = styles.getPropertyValue('--el-text-color-secondary').trim() || '#909399'
    const borderColor = styles.getPropertyValue('--el-border-color-lighter').trim() || '#ebeef5'
    return {
        animationDurationUpdate: 300,
        tooltip: {
            trigger: 'axis',
            confine: true,
            padding: 8,
            backgroundColor: styles.getPropertyValue('--el-bg-color-overlay').trim() || '#ffffff',
            borderColor: borderColor,
            textStyle: {
                color: styles.getPropertyValue('--el-text-color-primary').trim() || '#303133',
                fontSize: 12
            },
            formatter: params => {
                const title = formatTime(params[0]?.axisValue, true)
                const values = params.map(item =>
                    `${item.marker}${item.seriesName}: ${Number(item.value).toFixed(1)} ${config.unit || ''}`.trim()
                )
                return [title, ...values].filter(Boolean).join('<br>')
            }
        },
        grid: {
            left: '12',
            right: '16',
            bottom: '8',
            top: config.legend ? '44' : '34',
            containLabel: true
        },
        legend: config.legend ? {
            top: 0,
            right: 4,
            icon: 'roundRect',
            itemWidth: 14,
            itemHeight: 3,
            textStyle: {
                color: textColor,
                fontSize: 12
            }
        } : undefined,
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: dataX,
            axisLine: {
                lineStyle: {
                    color: borderColor
                }
            },
            axisTick: {
                show: false
            },
            axisLabel: {
                color: textColor,
                hideOverlap: true,
                formatter: value => formatTime(value)
            }
        },
        yAxis: {
            type: 'value',
            name: name,
            min: 0,
            max: config.max,
            splitNumber: 3,
            nameTextStyle: {
                color: textColor,
                align: 'left'
            },
            axisLabel: {
                color: textColor,
                formatter: value => Number(value).toFixed(config.decimals || 0)
            },
            splitLine: {
                lineStyle: {
                    color: borderColor
                }
            }
        }
    };
}

function singleSeries(option, name, dataY, colors, threshold) {
    option.series = [
        {
            name: name,
            type: 'line',
            sampling: 'lttb',
            showSymbol: false,
            smooth: 0.2,
            lineStyle: {
                width: 2,
                color: colors[0]
            },
            itemStyle: {
                color: colors[0]
            },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {
                        offset: 0,
                        color: colors[1]
                    }, {
                        offset: 1,
                        color: colors[2]
                    }
                ])
            },
            markLine: threshold ? {
                silent: true,
                symbol: 'none',
                label: {
                    formatter: `阈值 ${threshold}%`,
                    position: 'insideEndTop'
                },
                lineStyle: {
                    color: '#f56c6c',
                    type: 'dashed',
                    width: 1
                },
                data: [{yAxis: threshold}]
            } : undefined,
            data: dataY
        }
    ]
}

function doubleSeries(option, name, dataY, colors) {
    option.series = [
        {
            name: name[0],
            type: 'line',
            sampling: 'lttb',
            showSymbol: false,
            smooth: 0.2,
            lineStyle: {
                width: 2,
                color: colors[0]
            },
            itemStyle: {
                color: colors[0]
            },
            data: dataY[0]
        }, {
            name: name[1],
            type: 'line',
            sampling: 'lttb',
            showSymbol: false,
            smooth: 0.2,
            lineStyle: {
                width: 2,
                color: colors[1]
            },
            itemStyle: {
                color: colors[1]
            },
            data: dataY[1]
        }
    ]
}

export { defaultOption, singleSeries, doubleSeries }
