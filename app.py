# Horloge Dynamique — Mise à Jour en Temps Réel
st.components.v1.html("""
    <div style='padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); 
                border-radius: 12px; margin-bottom: 25px; 
                border-left: 5px solid #1E3A5F;
                box-shadow: 0 4px 12px rgba(30,58,95,0.1);'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
            <div style='flex: 1; min-width: 200px;'>
                <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                    📅 Date Actuelle
                </p>
                <p id='date' style='margin: 5px 0 0 0; font-size: 1.3em; font-weight: 600; color: #1E3A5F;'>
                    --/--/----
                </p>
            </div>
            
            <div style='flex: 1; min-width: 200px; text-align: center;'>
                <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                    🕐 Heure
                </p>
                <p id='time' style='margin: 5px 0 0 0; font-size: 2.5em; font-weight: 700; 
                                   color: #1E3A5F; font-family: monospace; letter-spacing: 2px;'>
                    --:--:--
                </p>
            </div>
            
            <div style='flex: 1; min-width: 200px; text-align: right;'>
                <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                    📊 État du Marché
                </p>
                <p id='status' style='margin: 10px 0 0 0; font-size: 1.2em; font-weight: 600; color: #6B7280;'>
                    ○ Vérification...
                </p>
                <p id='next-session' style='margin: 5px 0 0 0; font-size: 0.85em; color: #9CA3AF;'>
                    --
                </p>
            </div>
        </div>
        
        <!-- Barre de progression visuelle -->
        <div style='margin-top: 15px; background: #e5e7eb; border-radius: 10px; height: 8px; overflow: hidden;'>
            <div id='progress-bar' style='width: 0%; height: 100%; 
                                          background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
                                          transition: width 1s ease;'></div>
        </div>
    </div>
    
    <script>
    function updateClock() {
        const now = new Date();
        
        // Date formatée
        const dateOptions = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        document.getElementById('date').textContent = now.toLocaleDateString('fr-FR', dateOptions);
        
        // Heure formatée avec secondes (mise à jour chaque seconde)
        const timeString = now.toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
        document.getElementById('time').textContent = timeString;
        
        // État du marché
        const day = now.getDay(); // 0 = Dimanche, 6 = Samedi
        const hour = now.getHours();
        const minute = now.getMinutes();
        const currentTime = hour + minute / 60;
        
        const statusEl = document.getElementById('status');
        const nextSessionEl = document.getElementById('next-session');
        const progressBar = document.getElementById('progress-bar');
        
        // Vérifier si jour de bourse (Lundi-Vendredi)
        if (day >= 1 && day <= 5) {
            // Heures de bourse : 10h00 - 15h30
            const marketOpen = 10.0;
            const marketClose = 15.5;
            
            if (currentTime >= marketOpen && currentTime < marketClose) {
                // Marché ouvert
                statusEl.innerHTML = '● Marché Ouvert';
                statusEl.style.color = '#10B981';
                
                // Progression de la séance
                const progress = ((currentTime - marketOpen) / (marketClose - marketOpen)) * 100;
                progressBar.style.width = progress + '%';
                progressBar.style.background = 'linear-gradient(90deg, #10B981 0%, #34D399 100%)';
                
                nextSessionEl.textContent = `Fermeture dans ${Math.ceil(marketClose - currentTime)}h`;
            } else if (currentTime < marketOpen) {
                // Avant ouverture
                statusEl.innerHTML = '○ Marché Fermé';
                statusEl.style.color = '#F59E0B';
                progressBar.style.width = '0%';
                
                const hoursUntilOpen = marketOpen - currentTime;
                nextSessionEl.textContent = `Ouverture dans ${hoursUntilOpen.toFixed(1)}h`;
            } else {
                // Après fermeture
                statusEl.innerHTML = '○ Marché Fermé';
                statusEl.style.color = '#6B7280';
                progressBar.style.width = '100%';
                progressBar.style.background = 'linear-gradient(90deg, #6B7280 0%, #9CA3AF 100%)';
                
                // Prochain jour de bourse
                const nextOpen = new Date(now);
                nextOpen.setDate(now.getDate() + 1);
                if (nextOpen.getDay() === 6) nextOpen.setDate(nextOpen.getDate() + 1); // Skip Saturday
                if (nextOpen.getDay() === 0) nextOpen.setDate(nextOpen.getDate() + 1); // Skip Sunday
                nextSessionEl.textContent = `Prochaine séance: ${nextOpen.toLocaleDateString('fr-FR', {weekday: 'long', day: 'numeric', month: 'short'})}`;
            }
        } else {
            // Week-end
            statusEl.innerHTML = '○ Week-end';
            statusEl.style.color = '#6B7280';
            progressBar.style.width = '0%';
            
            const nextOpen = new Date(now);
            nextOpen.setDate(now.getDate() + (1 - now.getDay() + 7) % 7 || 7);
            nextSessionEl.textContent = `Reprise: ${nextOpen.toLocaleDateString('fr-FR', {weekday: 'long', day: 'numeric', month: 'short'})} à 10h00`;
        }
    }
    
    // Mise à jour immédiate
    updateClock();
    
    // Mise à jour chaque SECONDE (1000ms)
    setInterval(updateClock, 1000);
    
    // Animation fluide des secondes
    document.getElementById('time').style.transition = 'color 0.3s ease';
    setInterval(() => {
        const timeEl = document.getElementById('time');
        timeEl.style.color = '#1E3A5F';
        setTimeout(() => {
            timeEl.style.color = '#3B82F6';
        }, 100);
    }, 1000);
    </script>
""", height=180)
