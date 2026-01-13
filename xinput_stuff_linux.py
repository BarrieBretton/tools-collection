import subprocess as sp

xout = sp.check_output("xinput").decode().splitlines()
xout = [i.replace('⎡', '').replace('⎜', '').replace('⎣', '').replace('↳', '').strip() for i in xout]

mtouch = [i for i in xout if 'Multi-Touch' in i][0]
mtouch_id = int([i for i in mtouch.split() if 'id=' in i][0].lstrip('id='))

melan = [i for i in xout if 'Elantech' in i][0]
melan_id = int([i for i in melan.split() if 'id=' in i][0].lstrip('id='))

scroll_dist = sp.check_output(f'xinput --list-props {melan_id}'.split()).decode().splitlines()
syn = [i for i in scroll_dist if "Scrolling Distance" in i and not "Circular" in i][0]
syn_id = int([i for i in syn.split() if '(' in i][0].rstrip('):').lstrip('('))

print(f'xinput disable {mtouch_id}')
print(f'xinput set-prop {melan_id} {syn_id} -288, -288')

sp.Popen(f'xinput disable {mtouch_id}', shell=True)
sp.Popen(f'xinput set-prop {melan_id} {syn_id} -288, -288', shell=True)

