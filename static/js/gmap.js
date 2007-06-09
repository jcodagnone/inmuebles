// decide que API key de google map usar

var hostname = location.hostname;

if (hostname == "localhost") {
	key = 'ABQIAAAATukb-IKzfpX0wm2p69u_PhQz5JJ2zPi3YI9JDWBFF6NSsxhe4BR6cLQqQCNDkrEzrpibClKuSamdsw';
}else if(hostname == "alquiler.zauber.com.ar") {
	key = 'ABQIAAAATukb-IKzfpX0wm2p69u_PhTo6CZcd3oakdMBluQMkD69yr_eDhRt_1ixkleSp6ReUYMR9LQFXfNqDQ'
} else {
	alert('flof: no tenemos una API key para ' + hostname);
}

document.write("<script src='http://maps.google.com/maps?file=api&v=2&key=" + key + "' type='text/javascript'></script>");
