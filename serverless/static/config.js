module.exports = async ({ options, resolveVariable }) => {
    const custom = await resolveVariable('self:custom.var_files');
    let final = {}
    for (const val in custom) {
        final = {...final, ...custom[val]}
    }

    return final
  }
